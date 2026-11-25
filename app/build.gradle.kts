plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.dimm.skyline"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.dimm.skyline"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0-reconstruction"
    }
    buildTypes {
        debug { applicationIdSuffix = ".debug" }
        release { isMinifyEnabled = false; isShrinkResources = false }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
