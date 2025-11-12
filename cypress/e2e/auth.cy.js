function uniqueUsername() {
    return `test_${Date.now()}`
  }
  
  describe('Auth flow', () => {
    it('registers then logs in', () => {
      const username = uniqueUsername()
      const password = 'Passw0rd!'
  
      cy.visit('/register/')
      cy.url().should('include', '/register')
      
      cy.get('input[name="username"]').should('be.visible').type(username)
      cy.get('input[name="password1"]').should('be.visible').type(password)
      cy.get('input[name="password2"]').should('be.visible').type(password)
      
      cy.contains('button', /register/i).click()
      cy.wait(1000)
      
      // Check if we need to login manually
      cy.url().then((url) => {
        if (url.includes('/login')) {
          cy.get('input[name="username"]').type(username)
          cy.get('input[name="password"]').type(password)
          cy.contains('button', /login/i).click()
        }
      })
  
      cy.wait(1000)
      
      cy.url().should('not.include', '/login')
      
    })
  })