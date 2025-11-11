describe('Room lifecycle', () => {
    before(() => {
      cy.task('seed')   
    })
  
    it('creates a room, opens it, posts a message', () => {
      cy.visit('/')
  
      cy.contains(/login/i).click()
      cy.get('input[name="username"]').type('testuser')
      cy.get('input[name="password"]').type('password{enter}')
  
      cy.contains(/create room/i).click()
      cy.url().should('match', /create[-_]?room/)
  
      cy.get('input[name="topic"], select[name="topic"], [data-cy="topic"]')
        .should('exist')
        .then(($el) => {
          const el = $el[0]
          if (el.tagName.toLowerCase() === 'select') {
            cy.wrap($el).select('Django')
          } else {
            cy.wrap($el).clear().type('Django')
          }
        })
  
      cy.get('input[name="name"], [data-cy="room-name"]').clear().type('E2E Room')
      cy.get('textarea[name="description"], [data-cy="room-desc"]').clear().type('created by Cypress')
      cy.get('form').submit()
  
      cy.url().should('match', /room\/\d+\/?$/)
      cy.get('textarea[name="body"], [data-cy="message"]').type('hello from cypress{enter}')
      cy.contains(/hello from cypress/i).should('be.visible')
    })
  })
  