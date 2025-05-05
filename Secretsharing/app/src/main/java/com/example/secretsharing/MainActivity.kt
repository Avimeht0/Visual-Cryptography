package com.example.secretsharing

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.secretsharing.ui.theme.SecretSharingTheme
import com.example.secretsharing.ui.screens.HomeScreen
import com.example.secretsharing.ui.screens.ShareConstructionScreen
import com.example.secretsharing.ui.screens.ShareReconstructionScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SecretSharingTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    
                    NavHost(navController = navController, startDestination = "home") {
                        composable("home") { HomeScreen(navController) }
                        composable("share_construction") { ShareConstructionScreen(navController) }
                        composable("share_reconstruction") { ShareReconstructionScreen(navController) }
                    }
                }
            }
        }
    }
}