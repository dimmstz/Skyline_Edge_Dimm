#!/usr/bin/env python3
"""Replace upstream support branding with Skyline Dimm Pix support."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_dimm_pix_branding.py <strato-source-root>")
root = Path(sys.argv[1]).resolve()

def replace_once(path: Path, old: str, new: str):
    if not path.is_file():
        raise SystemExit(f"Required file missing: {path}")
    data = path.read_text(encoding="utf-8")
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{path.relative_to(root)}: expected one patch anchor, found {count}: {old[:100]!r}")
    path.write_text(data.replace(old, new, 1), encoding="utf-8")

main = root / "app/src/main/java/org/stratoemu/strato/MainActivity.kt"
source = main.read_text(encoding="utf-8")
source = source.replace("import android.graphics.Color\n", "import android.graphics.Bitmap\nimport android.graphics.Color\n")
source = source.replace("import android.view.View\n", "import android.view.View\nimport android.widget.ImageView\nimport android.content.ClipData\nimport android.content.ClipboardManager\nimport android.widget.Toast\n")
source = source.replace("import com.google.android.material.snackbar.Snackbar\n", "import com.google.android.material.snackbar.Snackbar\nimport com.google.zxing.BarcodeFormat\nimport com.google.zxing.qrcode.QRCodeWriter\n")
if "showKofiSupportDialog()" not in source:
    raise SystemExit("Original support dialog call not found")
source = source.replace("showKofiSupportDialog()", "showPixSupportDialog()", 1)
source = source.replace("private fun showKofiSupportDialog()", "private fun showPixSupportDialog()", 1)
start = source.index("    private fun showPixSupportDialog() {")
end = source.index("\n    private fun setAppListDecoration()", start)
new_function = r'''    private fun showPixSupportDialog() {
        val pixPayload = "00020101021126950014BR.GOV.BCB.PIX2573pix-qr.mercadopago.com/instore/ol/v2/ACzeYdm6HhM3K1kzfdCrLgPLNOammxPQ7YBJ5204000053039865802BR5916DIMM MULTIMARCAS6009SAO PAULO62080504mpis63042A77"
        val dialog = Dialog(this)
        dialog.setContentView(R.layout.dimm_pix_dialog)
        dialog.window?.setBackgroundDrawableResource(android.R.color.transparent)
        dialog.setCancelable(true)

        val matrix = QRCodeWriter().encode(pixPayload, BarcodeFormat.QR_CODE, 640, 640)
        val qrBitmap = Bitmap.createBitmap(matrix.width, matrix.height, Bitmap.Config.ARGB_8888)
        for (y in 0 until matrix.height) {
            for (x in 0 until matrix.width) {
                qrBitmap.setPixel(x, y, if (matrix[x, y]) Color.BLACK else Color.WHITE)
            }
        }
        dialog.findViewById<ImageView>(R.id.pix_qr_code).setImageBitmap(qrBitmap)
        dialog.findViewById<View>(R.id.pix_copy_button).setOnClickListener {
            val clipboard = getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("Pix Skyline Dimm", pixPayload))
            Toast.makeText(this, R.string.dimm_pix_copied, Toast.LENGTH_SHORT).show()
        }
        dialog.findViewById<View>(R.id.pix_close_button).setOnClickListener { dialog.dismiss() }

        dialog.show()
        val screenWidth = resources.displayMetrics.widthPixels
        val maxWidth = (430 * resources.displayMetrics.density).toInt()
        val margins = (40 * resources.displayMetrics.density).toInt()
        dialog.window?.setLayout((screenWidth - margins).coerceAtMost(maxWidth).coerceAtLeast(1),
                                 WindowManager.LayoutParams.WRAP_CONTENT)
    }
'''
source = source[:start] + new_function + source[end:]
main.write_text(source, encoding="utf-8")

layout = root / "app/src/main/res/layout/dimm_pix_dialog.xml"
layout.write_text('''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:fillViewport="false"
    android:background="@drawable/dimm_pix_dialog_background">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:gravity="center_horizontal"
        android:padding="22dp">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:gravity="center"
            android:text="💙"
            android:textSize="34sp" />

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="8dp"
            android:fontFamily="sans-serif-medium"
            android:gravity="center"
            android:text="@string/dimm_pix_title"
            android:textColor="#FFFFFFFF"
            android:textSize="23sp" />

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="10dp"
            android:gravity="center"
            android:lineSpacingExtra="4dp"
            android:text="@string/dimm_pix_message"
            android:textColor="#FFEAF3FF"
            android:textSize="14sp" />

        <ImageView
            android:id="@+id/pix_qr_code"
            android:layout_width="220dp"
            android:layout_height="220dp"
            android:layout_marginTop="18dp"
            android:padding="8dp"
            android:background="#FFFFFFFF"
            android:contentDescription="@string/dimm_pix_qr_description"
            android:scaleType="fitCenter" />

        <com.google.android.material.button.MaterialButton
            android:id="@+id/pix_copy_button"
            android:layout_width="match_parent"
            android:layout_height="52dp"
            android:layout_marginTop="18dp"
            android:text="@string/dimm_pix_copy"
            android:textAllCaps="false"
            android:textColor="#FF003071"
            android:textSize="15sp"
            app:backgroundTint="#FFFFFFFF"
            app:cornerRadius="24dp" />

        <com.google.android.material.button.MaterialButton
            android:id="@+id/pix_close_button"
            android:layout_width="match_parent"
            android:layout_height="48dp"
            android:layout_marginTop="7dp"
            android:text="@string/mali_kofi_not_now"
            android:textAllCaps="false"
            android:textColor="#FFFFFFFF"
            android:textSize="14sp"
            app:backgroundTint="#00255CE4"
            app:cornerRadius="24dp"
            app:strokeColor="#90BFEFFF"
            app:strokeWidth="1dp" />
    </LinearLayout>
</ScrollView>
''', encoding="utf-8")

drawable = root / "app/src/main/res/drawable/dimm_pix_dialog_background.xml"
drawable.write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:angle="135" android:startColor="#0A1F50" android:centerColor="#1252BC" android:endColor="#1774FF" />
    <corners android:radius="28dp" />
    <stroke android:width="1dp" android:color="#649FEFFF" />
</shape>
''', encoding="utf-8")

gradle = root / "app/build.gradle"
replace_once(gradle, "    /* Other Java */\n", "    /* Other Java */\n    implementation 'com.google.zxing:core:3.5.3'\n")
print("Applied Skyline Dimm Pix support dialog, offline QR generation and copy-to-clipboard.")
