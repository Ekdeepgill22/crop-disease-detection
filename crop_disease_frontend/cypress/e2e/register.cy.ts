/// <reference types="cypress" />

describe('Registration', () => {
  it('should allow a user to register with valid details', () => {
    cy.visit('/register');

    // Fill in the registration form
    cy.get('input[id="fullName"]').type('Test User');
    cy.get('input[id="email"]').type(`testuser_${Date.now()}@example.com`);
    cy.get('input[id="location"]').type('Test Farm');
    cy.get('input[id="password"]').type('password123');
    cy.get('input[id="confirmPassword"]').type('password123');

    // Agree to terms
    cy.get('input[id="terms"]').check();

    // Submit the form
    cy.get('button[type="submit"]').click();

    // Assert that the user is redirected to the dashboard
    cy.url().should('include', '/dashboard');

    // Assert that a welcome message is shown
    cy.contains('Registration Successful').should('be.visible');
  });
}); 