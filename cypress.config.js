const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://127.0.0.1:8000/',
    specPattern: 'cypress/e2e/**/*.cy.{js,ts}',
  },
  reporter: 'mocha-junit-reporter',
  reporterOptions: {
    mochaFile: 'reports/frontend/cypress-results-[hash].xml',  
    toConsole: true, 
  },
  video: true,
  screenshotOnRunFailure: true,
})