import tkinter as tk

resultado_mostrado = False

def agregar_valor(valor):
    global resultado_mostrado
    if resultado_mostrado:
        if valor in "+-*/":
            resultado_mostrado = False
        else:
            pantalla.delete(0, tk.END)
            resultado_mostrado = False
    pantalla.insert(tk.END, valor)

def calcular():
  global resultado_mostrado
  try:
      resultado = eval(pantalla.get())
      pantalla.delete(0, tk.END)
      pantalla.insert(tk.END, str(resultado))
      resultado_mostrado = True
  except:
      pantalla.delete(0, tk.END)
      pantalla.insert(tk.END, "Error")
      resultado_mostrado = True

def corregir():
    pantalla.delete(0, tk.END)

def borrar():
    contenido= pantalla.get()
    pantalla.delete(0, tk.END)
    pantalla.insert(0, contenido[:-1])



ventana = tk.Tk()
ventana.geometry("200x350")
ventana.title("Prueba")
ventana.configure(bg="#1c1a1a")
ventana.resizable(False, False)

ancho_ventana= 200
alto_ventana= 350

ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

x = (ancho_pantalla//2) - (ancho_ventana// 2)
y = (alto_pantalla//2) - (alto_ventana//2)

ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

etiqueta = tk.Label(ventana, text="Calculadora", font=("Impact", 20), bg="#1c1a1a", fg="white")
etiqueta.pack()

pantalla = tk.Entry(ventana, font=("Impact", 24, "bold"))
pantalla.place(x=10, y=100, width=180, height=40)

btn1= tk.Button(ventana, text="1", font=("Arial", 12, "bold"), bg="#8fff00", command=lambda: agregar_valor("1"))
btn1.place(x=10, y=180, width=24)
btn2= tk.Button(ventana, text="2", font=("Arial", 12, "bold"), bg="#8fff00", command=lambda: agregar_valor("2"))
btn2.place(x=40, y=180, width=24)
btn3 = tk.Button(ventana, text="3", font=("Arial", 12, "bold"), bg="#8fff00", command=lambda: agregar_valor("3"))
btn3.place(x=70, y=180, width=24)

btn4 = tk.Button(ventana, text="4", font=("Arial", 12, "bold"), bg="#fffafa", command=lambda: agregar_valor("4"))
btn4.place(x=10, y=220, width=24)
btn5 = tk.Button(ventana, text="5", font=("Arial", 12, "bold"), bg="#fffafa", command=lambda: agregar_valor("5"))
btn5.place(x=40, y=220, width=24)
btn6 = tk.Button(ventana, text="6", font=("Arial", 12, "bold"), bg="#fffafa", command=lambda: agregar_valor("6"))
btn6.place(x=70, y=220, width=24)

btn7 = tk.Button(ventana, text="7", font=("Arial", 12, "bold"), bg="#ff3737", command=lambda: agregar_valor("7"))
btn7.place(x=10, y=260, width=24)
btn8 = tk.Button(ventana, text="8", font=("Arial", 12, "bold"), bg="#ff3737", command=lambda: agregar_valor("8"))
btn8.place(x=40, y=260, width=24)
btn9 = tk.Button(ventana, text="9", font=("Arial", 12, "bold"), bg="#ff3737", command=lambda: agregar_valor("9"))
btn9.place(x=70, y=260, width=24)

btn0 = tk.Button(ventana, text="0", font=("Arial", 12, "bold"), bg="#00d1ff", command=lambda: agregar_valor("0"))
btn0.place(x=10, y=300, width=24)
btnPunto = tk.Button(ventana, text=".", font=("Arial", 12, "bold"), bg="#00d1ff", command=lambda: agregar_valor("."))
btnPunto.place(x=40, y=300, width=24)
btnIgual = tk.Button(ventana, text="=", font=("Arial", 12, "bold"), bg="#00d1ff", command=lambda: calcular())
btnIgual.place(x=70, y=300, width=24)

btnsum = tk.Button(ventana, text="+", font=("Arial", 12, "bold"), bg="#00d1ff", command=lambda: agregar_valor("+"))
btnsum.place(x=100, y=300, width=24)
btnrest = tk.Button(ventana, text="-", font=("Arial", 12, "bold"), bg="#ff3737", command=lambda: agregar_valor("-"))
btnrest.place(x=100, y=260, width=24)
btndiv = tk.Button(ventana, text="/", font=("Arial", 12, "bold"), bg="#fffafa", command=lambda: agregar_valor("/"))
btndiv.place(x=100, y=220, width=24)
btnmulti = tk.Button(ventana, text="*", font=("Arial", 12, "bold"), bg="#8fff00", command=lambda: agregar_valor("*"))
btnmulti.place(x=100, y=180, width=24)

btnCorregir = tk.Button(ventana, text="C", font=("Arial", 12, "bold"), bg="#00d1ff", command=lambda: corregir())
btnCorregir.place(x=130, y=300, width=24)
btnBorrar = tk.Button(ventana, text= "←", font=("Arial", 12, "bold"), bg="#ff3737", command=borrar)
btnBorrar.place(x=130, y=260, width=24)


ventana.mainloop()
