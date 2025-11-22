export function generateFakeVideoSummary(chunks) {
  const totalDuration = chunks.length * 30;

  return {
    resumen_global: `El video analizado tiene una duración total aproximada de ${totalDuration} segundos. Se identificaron patrones de movimiento, aperturas defensivas y momentos clave en varios segmentos.`,
    intervalos: chunks.map((c, i) => ({
      intervalo: `Segmento ${i + 1} (minuto ${i * 0.5} - ${i * 0.5 + 0.5})`,
      errores: [
        "Guarda baja en transiciones.",
        "Recuperación lenta después de jabs.",
      ],
      oportunidades: [
        "Ventana para contragolpe en retroceso.",
        "Apertura al atacar el lado débil del oponente.",
      ],
      intensidad: Math.floor(Math.random() * 100),
    })),
  };
}
