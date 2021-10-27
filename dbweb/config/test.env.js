'use strict'
const merge = require('webpack-merge')
const devEnv = require('./dev.env')

module.exports = merge(devEnv, {
  NODE_ENV: "'testing'",
  // BASE_API: "'http://192.168.8.154:8000'",
  // request_timeout: 12000
})
