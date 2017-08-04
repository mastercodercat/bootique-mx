var webpack = require('webpack');
var merge = require('webpack-merge');
var baseConfig = require('./webpack.base.config.js');

var webpackConfig = merge(baseConfig, {
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"testing"'
            }
        })
    ],
});

// no need for app entry during tests
delete webpackConfig.entry;

module.exports = webpackConfig;
