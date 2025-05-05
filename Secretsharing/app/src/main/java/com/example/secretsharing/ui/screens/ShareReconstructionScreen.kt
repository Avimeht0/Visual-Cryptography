package com.example.secretsharing.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
fun ShareReconstructionScreen(navController: NavController) {
    val viewModel: SecretSharingViewModel = viewModel()
    val context = LocalContext.current
    var selectedShares by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var k by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsState()

    val sharePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents()
    ) { uris: List<Uri> ->
        selectedShares = uris
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Share Reconstruction",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        Button(
            onClick = { sharePicker.launch("image/*") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Select Shares")
        }

        OutlinedTextField(
            value = k,
            onValueChange = { k = it },
            label = { Text("Number of shares to use (k)") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        )

        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            items(selectedShares) { uri ->
                Text(
                    text = uri.lastPathSegment ?: "Unknown file",
                    modifier = Modifier.padding(vertical = 4.dp)
                )
            }
        }

        Button(
            onClick = {
                k.toIntOrNull()?.let { kValue ->
                    if (selectedShares.size >= kValue) {
                        viewModel.reconstructImage(context, selectedShares.take(kValue))
                    }
                }
            },
            enabled = selectedShares.isNotEmpty() && k.isNotBlank() && k.toIntOrNull()?.let { it <= selectedShares.size } == true,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Reconstruct Image")
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