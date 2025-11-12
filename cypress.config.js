const { defineConfig } = require('cypress')
const allureWriter = require('@shelex/cypress-allure-plugin/writer')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://127.0.0.1:8000/',
    specPattern: 'cypress/e2e/**/*.cy.{js,ts}',
    setupNodeEvents(on, config) {
      allureWriter(on, config)
      return config
    },
  },
  reporter: 'mocha-junit-reporter',
  reporterOptions: {
    mochaFile: 'reports/frontend/cypress-results-[hash].xml',  
    toConsole: true, 
  },
  video: true,
  screenshotOnRunFailure: true,
})