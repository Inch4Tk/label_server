const path = require('path');

module.exports = {
    entry: [
        "./flask_label/static/jsx/app.js"
    ],
    output: {
        path: path.resolve(__dirname, "flask_label/static/dist/"),
        filename: "bundle.js"
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            },
            {
                test: /\.(scss)$/,
                use: [{
                    loader: 'style-loader', // inject CSS to page
                }, {
                    loader: 'css-loader', // translates CSS into CommonJS modules
                }, {
                    loader: 'postcss-loader', // Run post css actions
                    options: {
                        plugins: function () { // post css plugins, can be exported to postcss.config.js
                            return [
                                require('precss'),
                                require('autoprefixer')
                            ];
                        }
                    }
                }, {
                    loader: 'sass-loader' // compiles Sass to CSS
                }]
            },
            { test: /\.(png|jpg)$/, loader: 'url-loader?limit=5000000' }
        ]
    },
    plugins: [
    ],
    mode: "development"
};