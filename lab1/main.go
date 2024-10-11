package main

import (
	"fmt"
	"image"
	"image/color"
	"math"
	"strconv"
	"sync"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/widget"
)

type ColorWheel struct {
	widget.BaseWidget
	SelectedColor  color.Color
	OnColorChanged func(color.Color)

	diameter float32
	mu       sync.Mutex
}

func NewColorWheel(diameter float32) *ColorWheel {
	cw := &ColorWheel{diameter: diameter}
	cw.ExtendBaseWidget(cw)
	return cw
}

func (cw *ColorWheel) CreateRenderer() fyne.WidgetRenderer {
	cw.mu.Lock()
	defer cw.mu.Unlock()

	img := canvas.NewRaster(cw.draw)
	img.SetMinSize(fyne.NewSize(cw.diameter, cw.diameter))

	objects := []fyne.CanvasObject{img}
	return &colorWheelRenderer{cw: cw, img: img, objects: objects}
}

func (cw *ColorWheel) draw(w, h int) image.Image {
	img := image.NewRGBA(image.Rect(0, 0, w, h))

	cx, cy := float64(w)/2, float64(h)/2
	radius := math.Min(cx, cy)

	for x := 0; x < w; x++ {
		for y := 0; y < h; y++ {

			dx := float64(x) - cx
			dy := float64(y) - cy
			r := math.Hypot(dx, dy)
			if r <= radius {
				theta := math.Atan2(dy, dx)
				if theta < 0 {
					theta += 2 * math.Pi
				}
				h := theta / (2 * math.Pi)
				s := r / radius
				v := 1.0

				c := hsvToColor(h, s, v)
				img.Set(x, y, c)
			} else {
				img.Set(x, y, color.Transparent)
			}
		}
	}
	return img
}

func hsvToColor(h, s, v float64) color.Color {
	i := int(h * 6)
	f := h*6 - float64(i)
	p := v * (1 - s)
	q := v * (1 - f*s)
	t := v * (1 - (1-f)*s)

	var r, g, b float64
	switch i % 6 {
	case 0:
		r, g, b = v, t, p
	case 1:
		r, g, b = q, v, p
	case 2:
		r, g, b = p, v, t
	case 3:
		r, g, b = p, q, v
	case 4:
		r, g, b = t, p, v
	case 5:
		r, g, b = v, p, q
	}

	return color.NRGBA{
		R: uint8(r * 255),
		G: uint8(g * 255),
		B: uint8(b * 255),
		A: 255,
	}
}

func (cw *ColorWheel) MouseDown(e *desktop.MouseEvent) {
	cw.updateSelectedColor(e)
}

func (cw *ColorWheel) MouseUp(e *desktop.MouseEvent) {}

func (cw *ColorWheel) MouseMoved(e *desktop.MouseEvent) {
	cw.updateSelectedColor(e)
}

func (cw *ColorWheel) updateSelectedColor(e *desktop.MouseEvent) {
	cw.mu.Lock()
	defer cw.mu.Unlock()

	size := cw.Size()
	cx, cy := size.Width/2, size.Height/2
	dx := e.Position.X - cx
	dy := e.Position.Y - cy
	r := math.Hypot(float64(dx), float64(dy))
	radius := float64(math.Min(float64(cx), float64(cy)))

	if r <= radius {
		theta := math.Atan2(float64(dy), float64(dx))
		if theta < 0 {
			theta += 2 * math.Pi
		}
		h := theta / (2 * math.Pi)
		s := r / radius
		v := 1.0

		c := hsvToColor(h, s, v)
		cw.SelectedColor = c
		if cw.OnColorChanged != nil {
			cw.OnColorChanged(c)
		}
	}
}

type colorWheelRenderer struct {
	cw      *ColorWheel
	img     *canvas.Raster
	objects []fyne.CanvasObject
}

func (r *colorWheelRenderer) Layout(size fyne.Size) {
	r.img.Resize(size)
}

func (r *colorWheelRenderer) MinSize() fyne.Size {
	return fyne.NewSize(r.cw.diameter, r.cw.diameter)
}

func (r *colorWheelRenderer) Refresh() {
	r.img.Refresh()
}

func (r *colorWheelRenderer) BackgroundColor() color.Color {
	return color.Transparent
}

func (r *colorWheelRenderer) Objects() []fyne.CanvasObject {
	return r.objects
}

func (r *colorWheelRenderer) Destroy() {}

func main() {
	myApp := app.New()
	myWindow := myApp.NewWindow("Color Models")

	// Начальные значения цвета (белый)
	var r, g, b uint8 = 255, 255, 255
	c, m, yC, k := RGBToCMYK(float64(r), float64(g), float64(b))
	h, s, v := RGBToHLS(r, g, b)

	// Создание виджетов ввода для RGB
	rEntry := widget.NewEntry()
	rEntry.SetText("255")
	gEntry := widget.NewEntry()
	gEntry.SetText("255")
	bEntry := widget.NewEntry()
	bEntry.SetText("255")

	// Создание ползунков для RGB
	rSlider := widget.NewSlider(0, 255)
	rSlider.SetValue(255)
	gSlider := widget.NewSlider(0, 255)
	gSlider.SetValue(255)

	bSlider := widget.NewSlider(0, 255)
	bSlider.SetValue(255)

	// Создание виджетов ввода для CMYK
	cEntry := widget.NewEntry()
	cEntry.SetText(fmt.Sprintf("%.2f", c))
	mEntry := widget.NewEntry()
	mEntry.SetText(fmt.Sprintf("%.2f", m))
	yEntry := widget.NewEntry()
	yEntry.SetText(fmt.Sprintf("%.2f", yC))
	kEntry := widget.NewEntry()
	kEntry.SetText(fmt.Sprintf("%.2f", k))

	// Создание ползунков для CMYK
	cSlider := widget.NewSlider(0, 1)
	cSlider.SetValue(c)
	cSlider.Step = 0.01

	mSlider := widget.NewSlider(0, 1)
	mSlider.SetValue(m)
	mSlider.Step = 0.01

	ySlider := widget.NewSlider(0, 1)
	ySlider.SetValue(yC)
	ySlider.Step = 0.01

	kSlider := widget.NewSlider(0, 1)
	kSlider.SetValue(k)
	kSlider.Step = 0.01

	// Создание виджетов ввода для HLS
	hEntry := widget.NewEntry()
	hEntry.SetText(fmt.Sprintf("%.2f", h))
	sEntry := widget.NewEntry()
	sEntry.SetText(fmt.Sprintf("%.2f", s))
	vEntry := widget.NewEntry()
	vEntry.SetText(fmt.Sprintf("%.2f", v))

	// Создание ползунков для HLS
	hSlider := widget.NewSlider(0, 360)
	hSlider.SetValue(h)
	sSlider := widget.NewSlider(0, 1)
	sSlider.SetValue(s)
	sSlider.Step = 0.01

	vSlider := widget.NewSlider(0, 1)
	vSlider.SetValue(v)
	vSlider.Step = 0.01

	// Прямоугольник для отображения цвета
	colorRect := canvas.NewRectangle(&color.NRGBA{R: uint8(r), G: uint8(g), B: uint8(b), A: 255})
	colorRect.SetMinSize(fyne.NewSize(100, 100))

	// Функция обновления цвета
	updateColor := func() {
		colorRect.FillColor = &color.NRGBA{R: uint8(r), G: uint8(g), B: uint8(b), A: 255}
		colorRect.Refresh()
	}

	var updating bool

	// Функция обновления всех моделей
	updateModels := func(changedModel string) {
		updating = true
		defer func() { updating = false }()
		if changedModel == "RGB" {
			// Обновить CMYK
			c, m, yC, k = RGBToCMYK(float64(r), float64(g), float64(b))
			cEntry.SetText(fmt.Sprintf("%.2f", c))
			mEntry.SetText(fmt.Sprintf("%.2f", m))
			yEntry.SetText(fmt.Sprintf("%.2f", yC))
			kEntry.SetText(fmt.Sprintf("%.2f", k))
			cSlider.SetValue(c)
			mSlider.SetValue(m)
			ySlider.SetValue(yC)
			kSlider.SetValue(k)

			// Обновить HLS
			h, s, v = RGBToHLS(r, g, b)
			hEntry.SetText(fmt.Sprintf("%.2f", h))
			sEntry.SetText(fmt.Sprintf("%.2f", s))
			vEntry.SetText(fmt.Sprintf("%.2f", v))
			hSlider.SetValue(h)
			sSlider.SetValue(s)
			vSlider.SetValue(v)

		} else if changedModel == "CMYK" {
			// Обновить RGB
			r, g, b = CMYKToRGB(c, m, yC, k)
			rEntry.SetText(strconv.Itoa(int(r)))
			gEntry.SetText(strconv.Itoa(int(g)))
			bEntry.SetText(strconv.Itoa(int(b)))
			rSlider.SetValue(float64(r))
			gSlider.SetValue(float64(g))
			bSlider.SetValue(float64(b))

			// Обновить HLS
			h, s, v = RGBToHLS(r, g, b)
			hEntry.SetText(fmt.Sprintf("%.2f", h))
			sEntry.SetText(fmt.Sprintf("%.2f", s))
			vEntry.SetText(fmt.Sprintf("%.2f", v))
			hSlider.SetValue(h)
			sSlider.SetValue(s)
			vSlider.SetValue(v)

		} else if changedModel == "HLS" {
			// Обновить RGB
			r, g, b = HLSToRGB(h, s, v)
			rEntry.SetText(strconv.Itoa(int(r)))
			gEntry.SetText(strconv.Itoa(int(g)))
			bEntry.SetText(strconv.Itoa(int(b)))
			rSlider.SetValue(float64(r))
			gSlider.SetValue(float64(g))
			bSlider.SetValue(float64(b))

			// Обновить CMYK
			c, m, yC, k = RGBToCMYK(float64(r), float64(g), float64(b))
			cEntry.SetText(fmt.Sprintf("%.2f", c))
			mEntry.SetText(fmt.Sprintf("%.2f", m))
			yEntry.SetText(fmt.Sprintf("%.2f", yC))
			kEntry.SetText(fmt.Sprintf("%.2f", k))
			cSlider.SetValue(c)
			mSlider.SetValue(m)
			ySlider.SetValue(yC)
			kSlider.SetValue(k)
		}

		// Функция обновления цвета на экране
		updateColor()
	}

	// Обработка изменений в ползунках RGB
	rSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		r = uint8(val)
		rEntry.SetText(strconv.Itoa(int(r)))
		updateModels("RGB")
	}
	gSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		g = uint8(val)
		gEntry.SetText(strconv.Itoa(int(g)))
		updateModels("RGB")
	}
	bSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		b = uint8(val)
		bEntry.SetText(strconv.Itoa(int(b)))
		updateModels("RGB")
	}

	// Обработка изменений в полях ввода RGB
	rEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.Atoi(text)
		if err == nil && val >= 0 && val <= 255 {
			r = uint8(val)
			rSlider.SetValue(float64(r))
			updateModels("RGB")
		}
	}
	gEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.Atoi(text)
		if err == nil && val >= 0 && val <= 255 {
			g = uint8(val)
			gSlider.SetValue(float64(g))
			updateModels("RGB")
		}
	}
	bEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.Atoi(text)
		if err == nil && val >= 0 && val <= 255 {
			b = uint8(val)
			bSlider.SetValue(float64(b))
			updateModels("RGB")
		}
	}

	// Обработка изменений в ползунках CMYK
	cSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		c = val
		cEntry.SetText(fmt.Sprintf("%.2f", c))
		updateModels("CMYK")
	}
	mSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		m = val
		mEntry.SetText(fmt.Sprintf("%.2f", m))
		updateModels("CMYK")
	}
	ySlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		yC = val
		yEntry.SetText(fmt.Sprintf("%.2f", yC))
		updateModels("CMYK")
	}
	kSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		k = val
		kEntry.SetText(fmt.Sprintf("%.2f", k))
		updateModels("CMYK")
	}

	// Обработка изменений в полях ввода CMYK
	cEntry.OnChanged = func(text string) {
		if updating {
			return
		}

		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0 && val <= 1 {
			c = val
			cSlider.SetValue(c)
			updateModels("CMYK")
		}
	}
	mEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0 && val <= 1 {
			m = val
			mSlider.SetValue(m)
			updateModels("CMYK")
		}
	}
	yEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0 && val <= 1 {
			yC = val
			ySlider.SetValue(yC)
			updateModels("CMYK")
		}
	}
	kEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0 && val <= 1 {
			k = val
			kSlider.SetValue(k)
			updateModels("CMYK")
		}
	}

	// Обработка изменений в ползунках HLS
	hSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		h = val
		hEntry.SetText(strconv.FormatFloat(val, 'f', 1, 64))
		updateModels("HLS")
	}
	sSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		s = val
		sEntry.SetText(strconv.FormatFloat(val, 'f', 1, 64))
		updateModels("HLS")
	}
	vSlider.OnChanged = func(val float64) {
		if updating {
			return
		}
		v = val
		vEntry.SetText(strconv.FormatFloat(val, 'f', 1, 64))
		updateModels("HLS")
	}

	// Обработка изменений в полях ввода HLS
	hEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0.0 && val <= 360.0 {
			h = val
			hSlider.SetValue(h)
			updateModels("HLS")
		}
	}
	sEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0.0 && val <= 1.0 {
			s = val
			sSlider.SetValue(s)
			updateModels("HLS")
		}
	}
	vEntry.OnChanged = func(text string) {
		if updating {
			return
		}
		val, err := strconv.ParseFloat(text, 64)
		if err == nil && val >= 0.0 && val <= 1.0 {
			v = val
			vSlider.SetValue(v)
			updateModels("HLS")
		}
	}

	// Расположение виджетов
	rgbContent := container.NewVBox(
		widget.NewLabel("RGB"),
		container.NewGridWithColumns(3,
			container.NewVBox(
				widget.NewLabel("R"),
				rEntry,
				rSlider,
			),
			container.NewVBox(
				widget.NewLabel("G"),
				gEntry,
				gSlider,
			),
			container.NewVBox(
				widget.NewLabel("B"),
				bEntry,
				bSlider,
			),
		),
	)

	cmykContent := container.NewVBox(
		widget.NewLabel("CMYK"),
		container.NewGridWithColumns(4,
			container.NewVBox(
				widget.NewLabel("C"),
				cEntry,
				cSlider,
			),
			container.NewVBox(
				widget.NewLabel("M"),
				mEntry,
				mSlider,
			),
			container.NewVBox(
				widget.NewLabel("Y"),
				yEntry,
				ySlider,
			),
			container.NewVBox(
				widget.NewLabel("K"),
				kEntry,
				kSlider,
			),
		),
	)

	// Расположение виджетов для HLS
	hsvContent := container.NewVBox(
		widget.NewLabel("HLS"),
		container.NewGridWithColumns(3,
			container.NewVBox(
				widget.NewLabel("H"),
				hEntry,
				hSlider,
			),
			container.NewVBox(
				widget.NewLabel("L"),
				sEntry,
				sSlider,
			),
			container.NewVBox(
				widget.NewLabel("S"),
				vEntry,
				vSlider,
			),
		),
	)

	colorWheel := NewColorWheel(200)

	// Обработчик изменения цвета
	colorWheel.OnColorChanged = func(c color.Color) {
		if updating {
			return
		}
		r16, g16, b16, _ := c.RGBA()

		// Преобразуем их в 8-битные значения
		
		r = uint8(r16 >> 8)
		g = uint8(g16 >> 8)
		b = uint8(b16 >> 8)

		rEntry.SetText(strconv.Itoa(int(r)))
		gEntry.SetText(strconv.Itoa(int(g)))
		bEntry.SetText(strconv.Itoa(int(b)))
		rSlider.SetValue(float64(r))
		gSlider.SetValue(float64(g))
		bSlider.SetValue(float64(b))


		updateModels("RGB")
	}

	content := container.NewVBox(
		rgbContent,
		cmykContent,
		hsvContent,
		colorWheel,
		colorRect,
	)

	myWindow.SetContent(content)
	myWindow.Resize(fyne.NewSize(600, 600))
	myWindow.ShowAndRun()
}

// Функции преобразования цветов из предыдущего шага
// ...

// RGB to CMYK
func RGBToCMYK(r, g, b float64) (c, m, y, k float64) {
	r /= 255
	g /= 255
	b /= 255

	k = 1 - math.Max(r, math.Max(g, b))
	if k != 1 {
		c = (1 - r - k) / (1 - k)
		m = (1 - g - k) / (1 - k)
		y = (1 - b - k) / (1 - k)
	} else {
		c, m, y = 0, 0, 0
	}
	return
}

// CMYK to RGB
func CMYKToRGB(c, m, y, k float64) (r, g, b uint8) {
	rFloat := 255 * (1 - c) * (1 - k)
	gFloat := 255 * (1 - m) * (1 - k)
	bFloat := 255 * (1 - y) * (1 - k)
	r, g, b = uint8(rFloat), uint8(gFloat), uint8(bFloat)
	return
}

// RGB to HSV
func RGBToHSV(r, g, b uint8) (h, s, v float64) {
	rFloat := float64(r) / 255
	gFloat := float64(g) / 255
	bFloat := float64(b) / 255

	max := math.Max(rFloat, math.Max(gFloat, bFloat))
	min := math.Min(rFloat, math.Min(gFloat, bFloat))
	delta := max - min

	v = max

	if max != 0 {
		s = delta / max
	} else {
		s = 0
		h = -1
		return
	}

	if delta == 0 {
		h = 0
	} else if max == rFloat {
		h = (gFloat - bFloat) / delta
		if gFloat < bFloat {
			h += 6
		}
	} else if max == gFloat {
		h = (bFloat-rFloat)/delta + 2
	} else {
		h = (rFloat-gFloat)/delta + 4
	}

	h *= 60
	return
}

// HSV to RGB
func HSVToRGB(h, s, v float64) (r, g, b uint8) {
	if s == 0 {
		r = uint8(v * 255)
		g = r
		b = r
		return
	}

	h /= 60
	i := math.Floor(h)
	f := h - i
	p := v * (1 - s)
	q := v * (1 - s*f)
	t := v * (1 - s*(1-f))

	var rFloat, gFloat, bFloat float64
	switch int(i) % 6 {
	case 0:
		rFloat, gFloat, bFloat = v, t, p
	case 1:
		rFloat, gFloat, bFloat = q, v, p
	case 2:
		rFloat, gFloat, bFloat = p, v, t
	case 3:
		rFloat, gFloat, bFloat = p, q, v
	case 4:
		rFloat, gFloat, bFloat = t, p, v
	case 5:
		rFloat, gFloat, bFloat = v, p, q
	}

	r = uint8(rFloat * 255)
	g = uint8(gFloat * 255)
	b = uint8(bFloat * 255)
	return
}

// RGB to HLS
func RGBToHLS(r, g, b uint8) (h, l, s float64) {
    rFloat := float64(r) / 255
    gFloat := float64(g) / 255
    bFloat := float64(b) / 255

    max := math.Max(rFloat, math.Max(gFloat, bFloat))
    min := math.Min(rFloat, math.Min(gFloat, bFloat))
    l = (max + min) / 2

    if max == min {
        s = 0
        h = 0
    } else {
        delta := max - min
        if l < 0.5 {
            s = delta / (max + min)
        } else {
            s = delta / (2.0 - max - min)
        }

        switch max {
        case rFloat:
            h = (gFloat - bFloat) / delta
            if gFloat < bFloat {
                h += 6
            }
        case gFloat:
            h = (bFloat - rFloat)/delta + 2
        case bFloat:
            h = (rFloat - gFloat)/delta + 4
        }
        h *= 60
    }

    return
}

// HLS to RGB
func HLSToRGB(h, l, s float64) (r, g, b uint8) {
    var rFloat, gFloat, bFloat float64

    if s == 0 {
        rFloat, gFloat, bFloat = l, l, l
    } else {
        var q float64
        if l < 0.5 {
            q = l * (1 + s)
        } else {
            q = l + s - l*s
        }
        p := 2*l - q
        hk := h / 360

        tR := hk + 1.0/3.0
        tG := hk
        tB := hk - 1.0/3.0

        tR = adjustHue(tR)
        tG = adjustHue(tG)
        tB = adjustHue(tB)

        rFloat = hueToRGB(p, q, tR)
        gFloat = hueToRGB(p, q, tG)
        bFloat = hueToRGB(p, q, tB)
    }

    r = uint8(rFloat * 255)
    g = uint8(gFloat * 255)
    b = uint8(bFloat * 255)
    return
}

func adjustHue(t float64) float64 {
    if t < 0 {
        t += 1
    }
    if t > 1 {
        t -= 1
    }
    return t
}

func hueToRGB(p, q, t float64) float64 {
    if t < 1.0/6.0 {
        return p + (q-p)*6*t
    }
    if t < 1.0/2.0 {
        return q
    }
    if t < 2.0/3.0 {
        return p + (q-p)*(2.0/3.0 - t)*6
    }
    return p
}
