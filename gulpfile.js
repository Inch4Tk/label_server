// requirements

var gulp = require("gulp");
var gulpBrowser = require("gulp-browser");
var babelify = require("babelify");
var del = require("del");
var size = require("gulp-size");
var concat = require("gulp-concat");
var sourcemaps = require("gulp-sourcemaps");
var sass = require("gulp-sass")
var autoprefixer = require("gulp-autoprefixer");

// tasks
let transforms = [
    {
        transform: "babelify",
        options: { presets: ["env", "react"] }
    }
];

gulp.task("transform-jsx", function () {
    var stream = gulp.src(["./flask_label/static/jsx/*.jsx", "./flask_label/static/jsx/*.js"])
      .pipe(gulpBrowser.browserify(transforms))
      .pipe(concat("app.js"))
      .pipe(gulp.dest("./flask_label/static/dist/js/"))
      .pipe(size());
    return stream;
});

// Vendor js
let vendor_js_dev = [
    "./bower_components/react/react.development.js",
    "./bower_components/react/react-dom.development.js",
    "./bower_components/react/react-art.development.js",
]
gulp.task("transform-vendorjs-dev", function () {
    var stream = gulp.src(vendor_js_dev)
      .pipe(sourcemaps.init())
      .pipe(concat("vendor.js"))
      .pipe(sourcemaps.write("./sourcemaps/"))
      .pipe(gulp.dest("./flask_label/static/dist/js/"))
      .pipe(size());
    return stream;
});

let vendor_js_prod = [
    "./bower_components/react/react.production.js",
    "./bower_components/react/react-dom.production.js",
    "./bower_components/react/react-art.production.js",
]
gulp.task("transform-vendorjs-prod", function () {
    var stream = gulp.src(vendor_js_prod)
      .pipe(sourcemaps.init())
      .pipe(concat("vendor.js"))
      .pipe(sourcemaps.write("./sourcemaps/"))
      .pipe(gulp.dest("./flask_label/static/dist/js/"))
      .pipe(size());
    return stream;
});

// Compile scss to css
gulp.task("scss", function() {
    var autoprefixerOptions = {
        browsers: ['last 2 versions'],
    };

    var sassOptions = {
        includePaths: [

        ]
    };
    var stream = gulp.src('./flask_label/static/scss/*.scss')
      .pipe(sourcemaps.init())
      .pipe(sass(sassOptions))
      .pipe(autoprefixer(autoprefixerOptions))
      .pipe(sourcemaps.write('./sourcemaps/'))
      .pipe(gulp.dest('flask_label/static/dist/css/'))
      .pipe(size());
    return stream;
});

// Vendor css
let vendor_css = [
    "./bower_components/bootstrap/dist/css/bootstrap.css",
    "./bower_components/bootstrap/dist/css/bootstrap-grid.css",
    "./bower_components/bootstrap/dist/css/bootstrap-reboot.css",
];

gulp.task("vendor-css", function(){
    var stream = gulp.src(vendor_css)
      .pipe(sourcemaps.init())
      .pipe(concat("vendor.css"))
      .pipe(sourcemaps.write("./sourcemaps/"))
      .pipe(gulp.dest("./flask_label/static/dist/css/"))
      .pipe(size());
    return stream;
})


gulp.task("del-js", function () {
    return del(["./flask_label/static/scripts/dist/js"]);
});

gulp.task("del-css", function () {
    return del(["./flask_label/static/scripts/dist/css"]);
});

gulp.task("default", ["del-js", "del-css"], function () {
    gulp.start("transform-jsx");
    gulp.start("transform-vendorjs-dev")
    gulp.start("scss")
    gulp.start("vendor-css")
    gulp.watch("./flask_label/static/jsx/**/*.js", ["transform-jsx"]);
    gulp.watch("./flask_label/static/scss/**/*.scss", ["scss"]);
});