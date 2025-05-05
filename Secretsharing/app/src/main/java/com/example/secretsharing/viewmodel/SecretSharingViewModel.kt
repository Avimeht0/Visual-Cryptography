package com.example.secretsharing.viewmodel

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.net.Uri
import android.os.Environment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.Random

class SecretSharingViewModel : ViewModel() {
    private val random = Random()
    
    private val _uiState = MutableStateFlow<SecretSharingUiState>(SecretSharingUiState.Idle)
    val uiState: StateFlow<SecretSharingUiState> = _uiState

    fun generateShares(context: Context, imageUri: Uri, k: Int, n: Int, imageLabel: String) {
        viewModelScope.launch {
            _uiState.value = SecretSharingUiState.Loading
            try {
                withContext(Dispatchers.IO) {
                    val bitmap = context.contentResolver.openInputStream(imageUri)?.use {
                        BitmapFactory.decodeStream(it)
                    } ?: throw Exception("Failed to load image")

                    val binaryImage = convertToBinary(bitmap)
                    val (C0, C1) = constructMatrices(k)
                    val numSubpixels = C0[0].size
                    val height = binaryImage.size
                    val width = binaryImage[0].size
                    
                    val shares = Array(n) { Array(height) { IntArray(width * numSubpixels) } }
                    val H = List(n * k) { { _: Int -> random.nextInt(k) } }

                    for (i in 0 until height) {
                        for (j in 0 until width) {
                            val pixel = binaryImage[i][j]
                            val pattern = if (pixel == 0) C0 else C1
                            
                            val permutation = (0 until numSubpixels).toList().shuffled(random)
                            val permutedPattern = pattern.map { row ->
                                IntArray(numSubpixels) { col -> row[permutation[col]] }
                            }.toTypedArray()

                            for (participant in 0 until n) {
                                val h = H[random.nextInt(H.size)]
                                val rowIndex = h(participant)
                                System.arraycopy(
                                    permutedPattern[rowIndex], 0,
                                    shares[participant][i], j * numSubpixels,
                                    numSubpixels
                                )
                            }
                        }
                    }

                    // Create directory in public storage
                    val baseDir = File(
                        Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS),
                        "Secret Sharing"
                    )
                    val sharesDir = File(baseDir, "Shares")
                    sharesDir.mkdirs()
                    
                    // Create timestamped folder for this sharing session
                    val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
                    val sessionDir = File(sharesDir, "${imageLabel}_$timestamp")
                    sessionDir.mkdirs()

                    // Save shares
                    shares.forEachIndexed { index, share ->
                        val shareBitmap = shareToBitmap(share)
                        val shareFile = File(sessionDir, "Share_${index + 1}.png")
                        saveBitmap(shareBitmap, shareFile)
                    }

                    withContext(Dispatchers.Main) {
                        _uiState.value = SecretSharingUiState.Success(
                            "Shares saved to:\n${sessionDir.absolutePath}"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.value = SecretSharingUiState.Error(e.message ?: "Unknown error occurred")
            }
        }
    }

    fun reconstructImage(context: Context, shareUris: List<Uri>, originalShareDir: String? = null) {
        viewModelScope.launch {
            _uiState.value = SecretSharingUiState.Loading
            try {
                withContext(Dispatchers.IO) {
                    val shares = shareUris.map { uri ->
                        context.contentResolver.openInputStream(uri)?.use {
                            BitmapFactory.decodeStream(it)
                        } ?: throw Exception("Failed to load share")
                    }

                    val height = shares[0].height
                    val shareWidth = shares[0].width
                    val numSubpixels = findNumSubpixels(shares[0])
                    val width = shareWidth / numSubpixels
                    
                    val reconstructed = Array(height) { IntArray(width) }

                    for (i in 0 until height) {
                        for (j in 0 until width) {
                            var hasBlack = false
                            for (share in shares) {
                                for (subpixel in 0 until numSubpixels) {
                                    val x = j * numSubpixels + subpixel
                                    if (x < share.width) {
                                        val pixel = share.getPixel(x, i)
                                        if (Color.red(pixel) < 128) {
                                            hasBlack = true
                                            break
                                        }
                                    }
                                }
                                if (hasBlack) break
                            }
                            reconstructed[i][j] = if (hasBlack) 1 else 0
                        }
                    }

                    // Determine where to save the reconstructed image
                    val baseDir = File(
                        Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS),
                        "Secret Sharing"
                    )
                    val outputDir = if (originalShareDir != null) {
                        File(originalShareDir).parentFile ?: File(baseDir, "Reconstructed")
                    } else {
                        File(baseDir, "Reconstructed")
                    }
                    outputDir.mkdirs()

                    val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
                    val outputFile = File(outputDir, "Reconstructed_$timestamp.png")
                    
                    val reconstructedBitmap = binaryArrayToBitmap(reconstructed)
                    saveBitmap(reconstructedBitmap, outputFile)

                    withContext(Dispatchers.Main) {
                        _uiState.value = SecretSharingUiState.Success(
                            "Image reconstructed and saved to:\n${outputFile.absolutePath}"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.value = SecretSharingUiState.Error(e.message ?: "Unknown error occurred")
            }
        }
    }

    private fun findNumSubpixels(share: Bitmap): Int {
        // Find the first black pixel to determine subpixel pattern
        for (x in 0 until share.width) {
            for (y in 0 until share.height) {
                if (Color.red(share.getPixel(x, y)) < 128) {
                    // Find how many consecutive black pixels we have
                    var count = 1
                    while (x + count < share.width && 
                           Color.red(share.getPixel(x + count, y)) < 128) {
                        count++
                    }
                    return count
                }
            }
        }
        return 1 // Default if no black pixels found
    }

    private fun convertToBinary(bitmap: Bitmap): Array<IntArray> {
        val width = bitmap.width
        val height = bitmap.height
        val binary = Array(height) { IntArray(width) }
        
        for (y in 0 until height) {
            for (x in 0 until width) {
                val pixel = bitmap.getPixel(x, y)
                val gray = (0.299 * Color.red(pixel) +
                           0.587 * Color.green(pixel) +
                           0.114 * Color.blue(pixel))
                binary[y][x] = if (gray < 128) 1 else 0
            }
        }
        return binary
    }

    private fun constructMatrices(k: Int): Pair<Array<IntArray>, Array<IntArray>> {
        val evenSubsets = generateSubsets(k, true)
        val oddSubsets = generateSubsets(k, false)
        val numColumns = evenSubsets.size
        val C0 = Array(k) { IntArray(numColumns) }
        val C1 = Array(k) { IntArray(numColumns) }

        for (i in 0 until k) {
            for (j in evenSubsets.indices) {
                if (i in evenSubsets[j]) C0[i][j] = 1
            }
            for (j in oddSubsets.indices) {
                if (i in oddSubsets[j]) C1[i][j] = 1
            }
        }

        return Pair(C0, C1)
    }

    private fun generateSubsets(k: Int, isEven: Boolean): List<Set<Int>> {
        val elements = (0 until k).toList()
        val subsets = mutableListOf<Set<Int>>()
        for (r in if (isEven) 0..k step 2 else 1..k step 2) {
            elements.combinations(r).forEach { subset ->
                subsets.add(subset.toSet())
            }
        }
        return subsets
    }

    private fun <T> List<T>.combinations(r: Int): List<List<T>> {
        if (r == 0) return listOf(emptyList())
        if (r > size) return emptyList()
        if (r == size) return listOf(this)
        return drop(1).combinations(r - 1).map { it + first() } + drop(1).combinations(r)
    }

    private fun shareToBitmap(share: Array<IntArray>): Bitmap {
        val height = share.size
        val width = share[0].size
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        for (y in 0 until height) {
            for (x in 0 until width) {
                val color = if (share[y][x] == 1) Color.BLACK else Color.WHITE
                bitmap.setPixel(x, y, color)
            }
        }
        return bitmap
    }

    private fun binaryArrayToBitmap(array: Array<IntArray>): Bitmap {
        val height = array.size
        val width = array[0].size
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        for (y in 0 until height) {
            for (x in 0 until width) {
                val color = if (array[y][x] == 1) Color.BLACK else Color.WHITE
                bitmap.setPixel(x, y, color)
            }
        }
        return bitmap
    }

    private fun saveBitmap(bitmap: Bitmap, file: File) {
        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
    }
}

sealed class SecretSharingUiState {
    object Idle : SecretSharingUiState()
    object Loading : SecretSharingUiState()
    data class Success(val message: String) : SecretSharingUiState()
    data class Error(val message: String) : SecretSharingUiState()
}