package com.example.secretsharing.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.secretsharing.viewmodel.SecretSharingViewModel
import com.example.secretsharing.viewmodel.SecretSharingUiState

@Composable
fun ShareConstructionScreen(navController: NavController) {
    val viewModel: SecretSharingViewModel = viewModel()
    val context = LocalContext.current
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var imageLabel by remember { mutableStateOf("") }
    var k by remember { mutableStateOf("") }
    var n by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsState()

    val imagePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        selectedImageUri = uri
        uri?.let {
            imageLabel = it.lastPathSegment?.substringBeforeLast('.') ?: "image"
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Share Construction",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        Button(
            onClick = { imagePicker.launch("image/*") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(if (selectedImageUri == null) "Select Image" else "Change Image")
        }

        OutlinedTextField(
            value = imageLabel,
            onValueChange = { imageLabel = it },
            label = { Text("Image Label") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        )

        OutlinedTextField(
            value = k,
            onValueChange = { k = it },
            label = { Text("Minimum shares required (k)") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        )

        OutlinedTextField(
            value = n,
            onValueChange = { n = it },
            label = { Text("Total shares to generate (n)") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        )

        Button(
            onClick = {
                selectedImageUri?.let { uri ->
                    k.toIntOrNull()?.let { kValue ->
                        n.toIntOrNull()?.let { nValue ->
                            viewModel.generateShares(context, uri, kValue, nValue, imageLabel)
                        }
                    }
                }
            },
            enabled = selectedImageUri != null && imageLabel.isNotBlank() && k.isNotBlank() && n.isNotBlank(),
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Generate Shares")
        }

        when (uiState) {
            is SecretSharingUiState.Loading -> {
                CircularProgressIndicator(modifier = Modifier.padding(16.dp))
            }
            is SecretSharingUiState.Success -> {
                Text(
                    text = (uiState as SecretSharingUiState.Success).message,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(16.dp)
                )
            }
            is SecretSharingUiState.Error -> {
                Text(
                    text = (uiState as SecretSharingUiState.Error).message,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(16.dp)
                )
            }
            else -> {}
        }

        Button(
            onClick = { navController.popBackStack() },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Back")
        }
    }
} 