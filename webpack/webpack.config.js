var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require('extract-text-webpack-plugin')
var entrypoints = require('./entrypoints.js');

module.exports = {

    //the base directory (absolute path) for resolving the entry option
    context: __dirname,

    //the entry point we created earlier. Note that './' means
    //your current directory. You don't have to specify the extension  now,
    //because you will specify extensions later in the `resolve` section
    entry: entrypoints,

    output: {
        //where you want your compiled bundle to be stored
        path: path.resolve(__dirname, '../static/bundles/'),
        //naming convention webpack should use for your files
        filename: '[name]-[hash].js',
        //tell Django to use this url for loading webpack bundles
        publicPath: process.env.NODE_ENV === 'production' ?
            '/static/bundles/' :
            'http://localhost:8080/static/bundles/',
    },

    plugins: [
        new BundleTracker({filename: './webpack/webpack-stats.json'}),

        new ExtractTextPlugin('[name]-[hash].css'),

        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            "window.jQuery": "jquery",
            Utils: path.resolve(__dirname, '../frontend/js/utils.js'),
            RoutePlanningGantt: path.resolve(__dirname, '../frontend/js/gantt.js'),
            ComingDueList: path.resolve(__dirname, '../frontend/js/comingduelist.js'),
            HobbsForm: path.resolve(__dirname, '../frontend/js/hobbsform.js'),
        }),
    ],

    module: {
        rules: [
            {
                test: /\.jsx?$/,
                //we definitely don't want babel to transpile all the files in
                //node_modules. That would take a long time.
                exclude: /node_modules/,
                use: [
                    { loader: 'babel-loader' }
                ]
            },
            {
                test: /\.vue$/,
                use: [
                    { loader: 'vue-loader' }
                ]
            },
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader' })
            },
            {
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader!sass-loader' })
            },
            {
                test: /\.less$/,
                loader: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader!less-loader' })
            },
            {
                test: /\.jpg|png$/,
                loader: ExtractTextPlugin.extract({ use: 'file-loader' })
            },
            {
                test: /\.(eot|svg|ttf|woff|jpg|png)(\?v=\d+\.\d+\.\d+)?/,
                use: [
                    { loader: 'url-loader' }
                ]
            },
            {
                test: require.resolve('jquery'),
                use: [
                    {
                        loader: 'expose-loader',
                        options: 'jQuery',
                    },
                    {
                        loader: 'expose-loader',
                        options: '$',
                    }
                ]
            }
        ]
    },

    resolve: {
        //tells webpack where to look for modules
        modules: ['node_modules'],
        //extensions that should be used to resolve modules
        extensions: ['.js', '.css', '.scss'],
        alias: {
            'vue': 'vue/dist/vue.common.js',
            '@frontend': path.resolve(__dirname, '../frontend'),
            '@frontend_components': path.resolve(__dirname, '../frontend/vue/components'),
        }
    }
}
