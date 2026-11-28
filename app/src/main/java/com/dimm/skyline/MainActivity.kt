package com.dimm.skyline

import android.app.Activity
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/**
 * Visual shell for the Skyline Dimm reconstruction.
 *
 * This screen deliberately reports the integration state honestly: the native
 * reference APK is not the same thing as a native core integrated in this app.
 * Game launching and settings controls are not exposed until their real
 * implementations are connected.
 */
class MainActivity : Activity() {

    private val background = Color.rgb(9, 12, 18)
    private val surface = Color.rgb(18, 23, 33)
    private val surfaceRaised = Color.rgb(24, 31, 43)
    private val border = Color.rgb(42, 53, 69)
    private val primary = Color.rgb(119, 224, 198)
    private val textPrimary = Color.rgb(242, 246, 250)
    private val textSecondary = Color.rgb(157, 171, 188)
    private val textMuted = Color.rgb(111, 128, 148)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = background
        window.navigationBarColor = background
        window.decorView.systemUiVisibility = 0

        val page = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(18), dp(20), dp(30))
            setBackgroundColor(this@MainActivity.background)
        }

        page.addView(buildHeader())
        page.addView(space(24))
        page.addView(buildHero())
        page.addView(space(26))
        page.addView(sectionTitle("STATUS DO PROJETO", "Visão geral da reconstrução"))
        page.addView(space(12))
        page.addView(buildCoreStatus())
        page.addView(space(10))
        page.addView(buildDeviceStatus())
        page.addView(space(26))
        page.addView(sectionTitle("BIBLIOTECA", "Sua coleção começa aqui"))
        page.addView(space(12))
        page.addView(buildLibraryEmptyState())
        page.addView(space(26))
        page.addView(sectionTitle("PRÓXIMAS ETAPAS", "O que falta para jogar"))
        page.addView(space(12))
        page.addView(buildMilestones())
        page.addView(space(22))
        page.addView(buildFooter())

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            clipToPadding = false
            setBackgroundColor(this@MainActivity.background)
            isVerticalScrollBarEnabled = false
            addView(page)
        }
        setContentView(scroll)
    }

    private fun buildHeader(): View {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val mark = TextView(this).apply {
            text = "S"
            textSize = 23f
            setTextColor(Color.rgb(8, 22, 24))
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
            gravity = Gravity.CENTER
            background = rounded(primary, 16)
            layoutParams = LinearLayout.LayoutParams(dp(46), dp(46))
        }
        val titleBlock = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(12), 0, 0, 0)
            addView(label("SKYLINE", 11f, textMuted, true).apply { letterSpacing = 0.16f })
            addView(label("DIMM", 20f, textPrimary, true).apply { letterSpacing = 0.08f })
        }
        row.addView(mark)
        row.addView(titleBlock, LinearLayout.LayoutParams(0, -2, 1f))
        row.addView(pill("ANDROID", primary, Color.rgb(14, 35, 34)))
        return row
    }

    private fun buildHero(): View {
        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(22), dp(20), dp(20))
            background = gradient(
                intArrayOf(Color.rgb(25, 62, 65), Color.rgb(19, 35, 48), Color.rgb(20, 27, 40)),
                24
            )
        }
        card.addView(pill("RECONSTRUÇÃO EM ANDAMENTO", primary, Color.rgb(13, 42, 42)))
        card.addView(space(18))
        card.addView(label("Uma nova forma\nde jogar no Android.", 29f, textPrimary, true).apply {
            setLineSpacing(dp(2).toFloat(), 1f)
        })
        card.addView(space(10))
        card.addView(label(
            "Projeto independente baseado na arquitetura Skyline Edge 69, com foco em compatibilidade e desempenho mobile.",
            14f, Color.rgb(190, 207, 218), false
        ).apply { setLineSpacing(dp(4).toFloat(), 1f) })
        card.addView(space(20))
        val divider = View(this).apply { setBackgroundColor(0x33FFFFFF) }
        card.addView(divider, LinearLayout.LayoutParams(-1, dp(1)))
        card.addView(space(14))
        val bottom = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        bottom.addView(label("FOCO DE OTIMIZAÇÃO", 10f, Color.rgb(164, 195, 197), true),
            LinearLayout.LayoutParams(0, -2, 1f))
        bottom.addView(label("Galaxy M23 · Adreno 619", 12f, textPrimary, true))
        card.addView(bottom)
        return card
    }

    private fun buildCoreStatus(): View {
        val card = baseCard()
        card.addView(LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            addView(statusDot(Color.rgb(242, 190, 92)))
            val copy = LinearLayout(this@MainActivity).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(dp(11), 0, 0, 0)
                addView(label("Núcleo nativo", 16f, textPrimary, true))
                addView(space(4))
                addView(label("Referência compilada; integração no app pendente", 12f, textSecondary))
            }
            addView(copy, LinearLayout.LayoutParams(0, -2, 1f))
            addView(pill("EM INTEGRAÇÃO", Color.rgb(242, 190, 92), Color.rgb(54, 43, 25)))
        })
        card.addView(space(16))
        card.addView(label(
            "A biblioteca nativa já foi compilada em uma build de referência. Esta tela ainda não inicializa o emulador nem carrega jogos.",
            13f, textSecondary
        ).apply { setLineSpacing(dp(3).toFloat(), 1f) })
        return card
    }

    private fun buildDeviceStatus(): View {
        val card = baseCard()
        card.addView(label("DISPOSITIVO-ALVO", 10f, textMuted, true).apply { letterSpacing = 0.12f })
        card.addView(space(12))
        val row = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        row.addView(metric("SAMSUNG", "Galaxy M23"))
        row.addView(metric("GPU", "Adreno 619"))
        row.addView(metric("SISTEMA", "Android 14"))
        card.addView(row)
        card.addView(space(12))
        card.addView(label(
            "Compatibilidade declarada como objetivo de desenvolvimento; desempenho e estabilidade ainda dependem de testes no aparelho.",
            12f, textSecondary
        ))
        return card
    }

    private fun buildLibraryEmptyState(): View {
        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(dp(20), dp(24), dp(20), dp(24))
            background = rounded(surface, 20, border)
        }
        val icon = TextView(this).apply {
            text = "＋"
            textSize = 28f
            setTextColor(primary)
            gravity = Gravity.CENTER
            background = rounded(Color.rgb(27, 48, 52), 18)
            layoutParams = LinearLayout.LayoutParams(dp(56), dp(56))
        }
        card.addView(icon)
        card.addView(space(14))
        card.addView(label("Nenhum jogo adicionado", 16f, textPrimary, true))
        card.addView(space(7))
        card.addView(label(
            "A seleção por armazenamento e a abertura de jogos serão ativadas quando a ponte JNI estiver integrada.",
            13f, textSecondary
        ).apply {
            gravity = Gravity.CENTER
            setLineSpacing(dp(3).toFloat(), 1f)
        })
        return card
    }

    private fun buildMilestones(): View {
        val card = baseCard()
        milestone(card, "01", "Interface Android", "Tela inicial redesenhada e adaptável", true)
        milestone(card, "02", "Integração Kotlin / JNI / C++", "Conectar a Activity ao núcleo real", false)
        milestone(card, "03", "Biblioteca e permissões SAF", "Selecionar ROMs sem permissões amplas", false)
        milestone(card, "04", "Vulkan e Adreno 619", "Validar renderização, estabilidade e FPS no M23", false)
        return card
    }

    private fun buildFooter(): View {
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(dp(12), dp(12), dp(12), dp(12))
        }
        box.addView(label("SKYLINE DIMM  ·  PROJETO INDEPENDENTE", 10f, textMuted, true).apply {
            gravity = Gravity.CENTER
            letterSpacing = 0.06f
        })
        box.addView(space(5))
        box.addView(label("A interface não representa uma build funcional do emulador.", 11f, textMuted).apply {
            gravity = Gravity.CENTER
        })
        return box
    }

    private fun sectionTitle(kicker: String, title: String): View {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(label(kicker, 10f, primary, true).apply { letterSpacing = 0.14f })
            addView(space(5))
            addView(label(title, 19f, textPrimary, true))
        }
    }

    private fun baseCard(): LinearLayout = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(16), dp(17), dp(16), dp(17))
        background = rounded(surface, 20, border)
    }

    private fun metric(kicker: String, value: String): View {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, 0, dp(8), 0)
            addView(label(kicker, 9f, textMuted, true))
            addView(space(5))
            addView(label(value, 12f, textPrimary, true))
        }.also { it.layoutParams = LinearLayout.LayoutParams(0, -2, 1f) }
    }

    private fun milestone(parent: LinearLayout, number: String, title: String, detail: String, done: Boolean) {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, dp(7), 0, dp(7))
        }
        val numberView = TextView(this).apply {
            text = number
            textSize = 11f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setTextColor(if (done) Color.rgb(10, 35, 32) else textSecondary)
            background = rounded(if (done) primary else surfaceRaised, 10)
            layoutParams = LinearLayout.LayoutParams(dp(34), dp(34))
        }
        val copy = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(12), 0, 0, 0)
            addView(label(title, 14f, textPrimary, true))
            addView(space(3))
            addView(label(detail, 11f, textSecondary))
        }
        row.addView(numberView)
        row.addView(copy, LinearLayout.LayoutParams(0, -2, 1f))
        row.addView(label(if (done) "FEITO" else "PENDENTE", 9f,
            if (done) primary else textMuted, true))
        parent.addView(row)
    }

    private fun statusDot(color: Int): View = View(this).apply {
        background = rounded(color, 20)
        layoutParams = LinearLayout.LayoutParams(dp(9), dp(9))
    }

    private fun pill(value: String, foreground: Int, fill: Int): TextView =
        TextView(this).apply {
            text = value
            textSize = 9f
            typeface = Typeface.DEFAULT_BOLD
            letterSpacing = 0.06f
            setTextColor(foreground)
            gravity = Gravity.CENTER
            setPadding(dp(10), dp(7), dp(10), dp(7))
            background = rounded(fill, 30)
        }

    private fun label(value: String, size: Float, color: Int, bold: Boolean = false): TextView =
        TextView(this).apply {
            text = value
            textSize = size
            setTextColor(color)
            typeface = Typeface.create("sans-serif", if (bold) Typeface.BOLD else Typeface.NORMAL)
            includeFontPadding = true
        }

    private fun space(height: Int): View = View(this).apply {
        layoutParams = LinearLayout.LayoutParams(1, dp(height))
    }

    private fun rounded(color: Int, radius: Int, stroke: Int? = null): GradientDrawable =
        GradientDrawable().apply {
            setColor(color)
            cornerRadius = dp(radius).toFloat()
            if (stroke != null) setStroke(dp(1), stroke)
        }

    private fun gradient(colors: IntArray, radius: Int): GradientDrawable =
        GradientDrawable(GradientDrawable.Orientation.TL_BR, colors).apply {
            cornerRadius = dp(radius).toFloat()
        }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
}
