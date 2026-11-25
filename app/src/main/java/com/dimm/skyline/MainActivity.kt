package com.dimm.skyline

import android.app.Activity
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val density = resources.displayMetrics.density
        fun dp(value: Int) = (value * density).toInt()
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(32), dp(24), dp(24))
            setBackgroundColor(0xFF101318.toInt())
        }
        fun addText(value: String, size: Float, color: Int, bold: Boolean = false) {
            content.addView(TextView(this).apply {
                text = value
                textSize = size
                setTextColor(color)
                if (bold) setTypeface(typeface, android.graphics.Typeface.BOLD)
                setPadding(0, dp(8), 0, dp(8))
            })
        }
        addText("SKYLINE DIMM", 26f, 0xFFFFFFFF.toInt(), true)
        addText("Base de reconstrução Android do Edge 69", 14f, 0xFFB8C1CC.toInt())
        addText("Estado: ponte JNI correlacionada; núcleo ainda não integrado", 16f, 0xFF80CBC4.toInt(), true)
        addText(
            "O APK original contém DEX e bibliotecas nativas compiladas. Esta tela é uma base nova e não representa o código-fonte original recuperado.",
            14f, 0xFFE0E5EB.toInt()
        )
        addText("Próximas etapas", 18f, 0xFFFFFFFF.toInt(), true)
        addText(
            "1. Validar a base Skyline pública e seus submódulos.\n" +
                "2. Comparar as classes Android com o Edge 69.\n" +
                "3. Integrar o núcleo C++/Vulkan e a ponte JNI.\n" +
                "4. Testar inicialização e jogos no Galaxy M23.",
            14f, 0xFFB8C1CC.toInt()
        )
        setContentView(ScrollView(this).apply { addView(content) })
    }
}
