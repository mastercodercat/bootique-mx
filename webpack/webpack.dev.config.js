var webpack = require('webpack');
var merge = require('webpack-merge');
var BundleTracker = require('webpack-bundle-tracker')
var FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin');
var baseWebpackConfig = require('./webpack.base.config.js');

module.exports = merge(baseWebpackConfig, {
    devtool: '#cheap-module-eval-source-map',

    plugins: [
        new BundleTracker({filename: './webpack/webpack-stats.json'}),

        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"development"'
            }
        }),

        new webpack.NoEmitOnErrorsPlugin(),

        new FriendlyErrorsPlugin()
    ],
});
