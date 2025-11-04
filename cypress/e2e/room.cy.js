Cypress.Commands.add('login', (email = 'testuser@example.com', password = 'Passw0rd!') => {
    cy.visit('/login/')
    cy.get('input[name="email"]').type(email)
    cy.get('input[name="password"]').type(password)
    cy.get('button[type="submit"]').click()
    cy.wait(1000)
    cy.contains(/logout/i, { timeout: 10000 }).should('exist')
  })
  
  describe('Room lifecycle', () => {
    it('creates a room, opens it, posts a message', () => {
      // Login with email
      cy.login('hitesh@email.com', 'yourpassword') // Replace with valid credentials
      
      cy.visit('/create-room/')
      cy.url().should('include', '/create-room')
      
      cy.get('input[name="topic"]').type('Python')
      cy.get('input[name="name"]').type('Cypress Room')
      cy.get('textarea[name="description"]').type('Created by Cypress')
      
      // Click Submit button
      cy.contains('button', /submit/i).click()
      
      cy.wait(2000)
      
      cy.contains(/cypress room/i, { timeout: 10000 }).click({ force: true })
      cy.url().should('match', /\/room\/\d+\/?$/)
      cy.get('input[name="body"]').type('Hello from Cypress!{Enter}')
      
    //   cy.get('input[name="body"]').closest('form').within(() => {
    //     cy.contains('button', /send/i).click()
    //   })
      
      cy.wait(500)
      
      cy.contains(/hello from cypress!/i).should('be.visible')
    })
  })