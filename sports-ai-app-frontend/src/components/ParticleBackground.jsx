import { useEffect } from "react";

export default function ParticleBackground() {
  useEffect(() => {
    const canvas = document.getElementById("particle-canvas");
    const ctx = canvas.getContext("2d");

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    class Particle {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = Math.random() * 2 + 2;
        this.color = neonColor();
        this.velX = (Math.random() - 0.3) * 3;
        this.velY = (Math.random() - 0.3) * 3;
        this.life = 0.5 + Math.random() * 0.5;
      }
      update() {
        this.x += this.velX;
        this.y += this.velY;
        this.size *= 0.95;
        this.life -= 0.02;
      }
      draw() {
        ctx.beginPath();
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 15;
        ctx.shadowColor = this.color;
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function neonColor() {
        const colors = [
            "#FFA552", // naranja neón suave
            "#FFB56B", // durazno neón
            "#FF9E4D", // naranja cálido
            "#FF8F3B", // mandarina neón
            "#FFC878", // naranja claro brillante
        ];
        return colors[Math.floor(Math.random() * colors.length)];
        }


    let particles = [];
    let animationFrameId;

    const handleMouseMove = (e) => {
      for (let i = 0; i < 3; i++) { // Reduced from 6 to 3 for performance
        particles.push(new Particle(e.clientX, e.clientY));
      }
    };

    window.addEventListener("mousemove", handleMouseMove);

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles = particles.filter((p) => p.life > 0 && p.size > 0.5);

      particles.forEach((p) => {
        p.update();
        p.draw();
      });

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      id="particle-canvas"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: -1,
        pointerEvents: "none",
      }}
    ></canvas>
  );
}
