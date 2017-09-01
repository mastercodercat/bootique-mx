var webpack = require('webpack');
var merge = require('webpack-merge');
var BundleTracker = require('webpack-bundle-tracker')
var FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin');
var baseWebpackConfig = require('./webpack.base.config.js');

module.exports = merge(baseWebpackConfig, {
    devtool: '#cheap-module-eval-source-map',

    plugins: [
        new BundleTracker({filename: './webpack/webpack-stats.json'}),

        // TODO: temporarliy disabled uglifying as it kills build process, need to find out why
        // new webpack.optimize.UglifyJsPlugin({
        //     sourceMap: false,
        // }),

        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"'
            }
        }),
    ],
});
