/**
 * API Communication Layer for MITRE ATT&CK MCP Explorer
 * 
 * This module provides a comprehensive API client for communicating with the
 * HTTP proxy server, including proper error handling, timeout management,
 * and retry logic for failed requests.
 */

class APIError extends Error {
    constructor(message, status = null, response = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
    }
}

class API {
    constructor(options = {}) {
        this.baseURL = options.baseURL || '';
        this.timeout = options.timeout || 30000; // 30 seconds default
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000; // 1 second default
        this.retryBackoff = options.retryBackoff || 2; // Exponential backoff multiplier
    }

    /**
     * Make an HTTP request with timeout, retry logic, and error handling
     * @param {string} url - The URL to request
     * @param {Object} options - Fetch options
     * @param {number} retryCount - Current retry attempt (internal use)
     * @returns {Promise<Response>} - The fetch response
     */
    async _makeRequest(url, options = {}, retryCount = 0) {
        // Create AbortController for timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            // Add abort signal to options
            const requestOptions = {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            };

            const response = await fetch(url, requestOptions);
            clearTimeout(timeoutId);

            // Check if response is ok
            if (!response.ok) {
                const errorText = await response.text();
                throw new APIError(
                    `HTTP ${response.status}: ${errorText || response.statusText}`,
                    response.status,
                    response
                );
            }

            return response;

        } catch (error) {
            clearTimeout(timeoutId);

            // Handle timeout errors
            if (error.name === 'AbortError') {
                throw new APIError(`Request timeout after ${this.timeout}ms`, 408);
            }

            // Handle network errors and retry logic
            if (this._shouldRetry(error, retryCount)) {
                const delay = this.retryDelay * Math.pow(this.retryBackoff, retryCount);
                console.warn(`Request failed, retrying in ${delay}ms... (attempt ${retryCount + 1}/${this.maxRetries})`);
                
                await this._sleep(delay);
                return this._makeRequest(url, options, retryCount + 1);
            }

            // Re-throw the error if we can't retry
            throw error;
        }
    }

    /**
     * Determine if a request should be retried
     * @param {Error} error - The error that occurred
     * @param {number} retryCount - Current retry count
     * @returns {boolean} - Whether to retry the request
     */
    _shouldRetry(error, retryCount) {
        // Don't retry if we've exceeded max retries
        if (retryCount >= this.maxRetries) {
            return false;
        }

        // Don't retry client errors (4xx), except for 408 (timeout) and 429 (rate limit)
        if (error instanceof APIError && error.status) {
            if (error.status >= 400 && error.status < 500) {
                return error.status === 408 || error.status === 429;
            }
        }

        // Retry network errors and server errors (5xx)
        return error.name === 'TypeError' || // Network error
               error.name === 'AbortError' || // Timeout
               (error instanceof APIError && error.status >= 500);
    }

    /**
     * Sleep for a specified number of milliseconds
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise<void>}
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get comprehensive system information
     * @returns {Promise<Object>} - System information object
     */
    async getSystemInfo() {
        try {
            const response = await this._makeRequest('/system_info');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch system info:', error);
            throw new APIError(`Failed to fetch system information: ${error.message}`);
        }
    }

    /**
     * Get list of available MCP tools
     * @returns {Promise<Array>} - Array of tool objects
     */
    async getTools() {
        try {
            const response = await this._makeRequest('/tools');
            const data = await response.json();
            return data.tools || [];
        } catch (error) {
            console.error('Failed to fetch tools:', error);
            throw new APIError(`Failed to fetch tools list: ${error.message}`);
        }
    }

    /**
     * Get list of threat groups for dropdown population
     * @returns {Promise<Array>} - Array of group objects
     */
    async getGroups() {
        try {
            const response = await this._makeRequest('/api/groups');
            const data = await response.json();
            return data.groups || [];
        } catch (error) {
            console.error('Failed to fetch groups:', error);
            throw new APIError(`Failed to fetch threat groups: ${error.message}`);
        }
    }

    /**
     * Get list of tactics for dropdown population
     * @returns {Promise<Array>} - Array of tactic objects
     */
    async getTactics() {
        try {
            const response = await this._makeRequest('/api/tactics');
            const data = await response.json();
            return data.tactics || [];
        } catch (error) {
            console.error('Failed to fetch tactics:', error);
            throw new APIError(`Failed to fetch tactics: ${error.message}`);
        }
    }

    /**
     * Get techniques for autocomplete functionality
     * @param {string} query - Search query string
     * @returns {Promise<Array>} - Array of matching technique objects
     */
    async getTechniques(query) {
        if (!query || typeof query !== 'string') {
            throw new APIError('Query parameter is required and must be a string');
        }

        if (query.length < 2) {
            throw new APIError('Query must be at least 2 characters long');
        }

        try {
            const encodedQuery = encodeURIComponent(query);
            const response = await this._makeRequest(`/api/techniques?q=${encodedQuery}`);
            const data = await response.json();
            return data.techniques || [];
        } catch (error) {
            console.error('Failed to fetch techniques:', error);
            throw new APIError(`Failed to fetch techniques: ${error.message}`);
        }
    }

    /**
     * Execute an MCP tool with the given parameters
     * @param {string} toolName - Name of the tool to execute
     * @param {Object} parameters - Parameters to pass to the tool
     * @returns {Promise<string>} - Tool execution result as text
     */
    async callTool(toolName, parameters = {}) {
        if (!toolName || typeof toolName !== 'string') {
            throw new APIError('Tool name is required and must be a string');
        }

        if (typeof parameters !== 'object' || parameters === null) {
            throw new APIError('Parameters must be an object');
        }

        try {
            const requestBody = {
                tool_name: toolName,
                parameters: parameters
            };

            const response = await this._makeRequest('/call_tool', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            // The response is plain text, not JSON
            return await response.text();

        } catch (error) {
            console.error(`Failed to execute tool ${toolName}:`, error);
            throw new APIError(`Failed to execute tool ${toolName}: ${error.message}`);
        }
    }

    /**
     * Check if the server is reachable and responsive
     * @returns {Promise<boolean>} - True if server is responsive
     */
    async checkConnection() {
        try {
            const response = await this._makeRequest('/tools', {}, 0); // No retries for connection check
            return response.ok;
        } catch (error) {
            console.warn('Connection check failed:', error.message);
            return false;
        }
    }

    /**
     * Get server health status with detailed information
     * @returns {Promise<Object>} - Health status object
     */
    async getHealthStatus() {
        try {
            const [systemInfo, toolsAvailable] = await Promise.allSettled([
                this.getSystemInfo(),
                this.getTools()
            ]);

            return {
                connected: true,
                systemInfo: systemInfo.status === 'fulfilled' ? systemInfo.value : null,
                toolsCount: toolsAvailable.status === 'fulfilled' ? toolsAvailable.value.length : 0,
                errors: [
                    ...(systemInfo.status === 'rejected' ? [`System info: ${systemInfo.reason.message}`] : []),
                    ...(toolsAvailable.status === 'rejected' ? [`Tools: ${toolsAvailable.reason.message}`] : [])
                ]
            };
        } catch (error) {
            return {
                connected: false,
                systemInfo: null,
                toolsCount: 0,
                errors: [error.message]
            };
        }
    }

    /**
     * Batch execute multiple tools with error handling
     * @param {Array} toolCalls - Array of {toolName, parameters} objects
     * @returns {Promise<Array>} - Array of results or errors
     */
    async batchCallTools(toolCalls) {
        if (!Array.isArray(toolCalls)) {
            throw new APIError('Tool calls must be an array');
        }

        const promises = toolCalls.map(async (call, index) => {
            try {
                const result = await this.callTool(call.toolName, call.parameters);
                return { index, success: true, result };
            } catch (error) {
                return { index, success: false, error: error.message };
            }
        });

        return Promise.all(promises);
    }

    /**
     * Validate tool parameters against tool schema
     * @param {string} toolName - Name of the tool
     * @param {Object} parameters - Parameters to validate
     * @returns {Promise<Object>} - Validation result
     */
    async validateToolParameters(toolName, parameters) {
        try {
            const tools = await this.getTools();
            const tool = tools.find(t => t.name === toolName);
            
            if (!tool) {
                return {
                    valid: false,
                    errors: [`Tool '${toolName}' not found`]
                };
            }

            const schema = tool.inputSchema;
            const errors = [];

            // Check required parameters
            if (schema.required) {
                for (const requiredParam of schema.required) {
                    if (!(requiredParam in parameters) || parameters[requiredParam] === null || parameters[requiredParam] === undefined) {
                        errors.push(`Required parameter '${requiredParam}' is missing`);
                    }
                }
            }

            // Basic type checking for provided parameters
            if (schema.properties) {
                for (const [paramName, paramValue] of Object.entries(parameters)) {
                    const paramSchema = schema.properties[paramName];
                    if (paramSchema) {
                        if (paramSchema.type === 'array' && !Array.isArray(paramValue)) {
                            errors.push(`Parameter '${paramName}' must be an array`);
                        } else if (paramSchema.type === 'string' && typeof paramValue !== 'string') {
                            errors.push(`Parameter '${paramName}' must be a string`);
                        } else if (paramSchema.type === 'integer' && !Number.isInteger(paramValue)) {
                            errors.push(`Parameter '${paramName}' must be an integer`);
                        }
                    }
                }
            }

            return {
                valid: errors.length === 0,
                errors
            };

        } catch (error) {
            return {
                valid: false,
                errors: [`Validation failed: ${error.message}`]
            };
        }
    }
}

// Create a default API instance
const api = new API();

// Export both the class and default instance
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = { API, APIError, api };
} else {
    // Browser environment - attach to window
    window.API = API;
    window.APIError = APIError;
    window.api = api;
}