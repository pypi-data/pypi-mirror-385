/**
 * Portfolio business logic - testable functions
 * Extracted from the MCP server for better testability and coverage
 */

import { McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';

/**
 * Search portfolio data by query, category, and limit
 */
export async function searchPortfolio(portfolioData, args) {
  const { query, category, limit = 10 } = args;
  const searchTerm = query.toLowerCase();

  let results = portfolioData.filter(item => {
    // Filter by category if specified
    if (category && item.category.toLowerCase() !== category.toLowerCase()) {
      return false;
    }

    // Search in title, description, and keywords
    const searchableText = [
      item.title,
      item.description,
      ...item.keywords
    ].join(' ').toLowerCase();

    return searchableText.includes(searchTerm);
  });

  // Limit results
  results = results.slice(0, limit);

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          query: query,
          category: category || 'all',
          resultsCount: results.length,
          results: results
        }, null, 2)
      }
    ]
  };
}

/**
 * Get all unique categories from portfolio data
 */
export async function getPortfolioCategories(portfolioData) {
  const categories = [...new Set(portfolioData.map(item => item.category))];

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          categories: categories,
          totalItems: portfolioData.length
        }, null, 2)
      }
    ]
  };
}

/**
 * Get a specific portfolio item by ID
 */
export async function getPortfolioItem(portfolioData, args) {
  const { id } = args;
  const item = portfolioData.find(item => item.id === id);

  if (!item) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Portfolio item with ID ${id} not found`
    );
  }

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(item, null, 2)
      }
    ]
  };
}

/**
 * Get all contact information
 */
export async function getContactInfo(portfolioData) {
  const contactItems = portfolioData.filter(item => item.category === 'Contact');

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          contact: contactItems
        }, null, 2)
      }
    ]
  };
}

/**
 * Get tech stack information, optionally filtered by type
 */
export async function getTechStack(portfolioData, args) {
  const { type } = args;
  let techItems = portfolioData.filter(item => item.category === 'Tech Stack');

  if (type) {
    techItems = techItems.filter(item =>
      item.title.toLowerCase().includes(type.toLowerCase())
    );
  }

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          techStack: techItems,
          filterType: type || 'all'
        }, null, 2)
      }
    ]
  };
}
