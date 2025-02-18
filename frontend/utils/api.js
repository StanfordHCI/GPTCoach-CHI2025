// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// Utility function to make authenticated requests
const makeAuthenticatedRequest = async (url, method = 'GET', body = null) => {
    const token = localStorage.getItem('token'); // Retrieve the stored token
    const headers = new Headers({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
    });
  
    const config = {
      method: method,
      headers: headers,
    };
  
    if (body) {
      config.body = JSON.stringify(body);
    }
  
    try {
      const response = await fetch(url, config);
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json(); // or handle based on your backend response
    } catch (error) {
      console.error("Failed to fetch:", error);
      throw error;
    }
  };

  export { makeAuthenticatedRequest };
