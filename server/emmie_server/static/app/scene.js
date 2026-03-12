const GRID_SPACING = 54;


function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}


function hexToRgba(hex, alpha) {
  const normalized = hex.replace("#", "");
  const red = Number.parseInt(normalized.slice(0, 2), 16);
  const green = Number.parseInt(normalized.slice(2, 4), 16);
  const blue = Number.parseInt(normalized.slice(4, 6), 16);
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}


export class SceneRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.context = canvas.getContext("2d");
    this.nodes = [];
    this.ripples = [];
    this.pointer = { x: 0.5, y: 0.5, active: false };
    this.animationFrame = 0;
    this.lastTimestamp = 0;
    this.pixelRatio = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    this.resizeObserver = new ResizeObserver(() => this.resize());

    this.handlePointerMove = this.handlePointerMove.bind(this);
    this.handlePointerDown = this.handlePointerDown.bind(this);
    this.handlePointerLeave = this.handlePointerLeave.bind(this);
    this.render = this.render.bind(this);

    canvas.addEventListener("pointermove", this.handlePointerMove);
    canvas.addEventListener("pointerdown", this.handlePointerDown);
    canvas.addEventListener("pointerleave", this.handlePointerLeave);
    this.resizeObserver.observe(canvas);
    this.resize();
    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  setNodes(nodes) {
    this.nodes = nodes.map((node, index) => ({
      ...node,
      phase: index * 0.9,
    }));
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = Math.floor(rect.width * this.pixelRatio);
    this.canvas.height = Math.floor(rect.height * this.pixelRatio);
    this.context.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
  }

  destroy() {
    window.cancelAnimationFrame(this.animationFrame);
    this.resizeObserver.disconnect();
    this.canvas.removeEventListener("pointermove", this.handlePointerMove);
    this.canvas.removeEventListener("pointerdown", this.handlePointerDown);
    this.canvas.removeEventListener("pointerleave", this.handlePointerLeave);
  }

  handlePointerMove(event) {
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = clamp((event.clientX - rect.left) / rect.width, 0, 1);
    this.pointer.y = clamp((event.clientY - rect.top) / rect.height, 0, 1);
    this.pointer.active = true;
  }

  handlePointerDown(event) {
    this.handlePointerMove(event);
    const colors = this.nodes.length > 0 ? this.nodes.map((node) => node.accent_color) : ["#72d1c2"];
    const color = colors[Math.floor(Math.random() * colors.length)];
    this.ripples.push({
      x: this.pointer.x,
      y: this.pointer.y,
      life: 0,
      color,
    });
  }

  handlePointerLeave() {
    this.pointer.active = false;
  }

  render(timestamp) {
    const elapsed = timestamp * 0.001;
    const delta = Math.min(0.033, (timestamp - this.lastTimestamp) * 0.001 || 0.016);
    this.lastTimestamp = timestamp;

    this.drawBackdrop(elapsed);
    this.drawGrid(elapsed);
    this.drawNodes(elapsed);
    this.drawRipples(delta);

    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  drawBackdrop(time) {
    const gradient = this.context.createLinearGradient(0, 0, this.width, this.height);
    gradient.addColorStop(0, "#091320");
    gradient.addColorStop(0.5, "#132033");
    gradient.addColorStop(1, "#263554");
    this.context.fillStyle = gradient;
    this.context.fillRect(0, 0, this.width, this.height);

    const glow = this.context.createRadialGradient(
      this.width * (0.22 + this.pointer.x * 0.08),
      this.height * (0.18 + this.pointer.y * 0.08),
      10,
      this.width * (0.22 + this.pointer.x * 0.08),
      this.height * (0.18 + this.pointer.y * 0.08),
      this.width * 0.65,
    );
    glow.addColorStop(0, "rgba(114, 209, 194, 0.18)");
    glow.addColorStop(0.5, "rgba(245, 154, 98, 0.08)");
    glow.addColorStop(1, "rgba(0, 0, 0, 0)");
    this.context.fillStyle = glow;
    this.context.fillRect(0, 0, this.width, this.height);

    for (let index = 0; index < 14; index += 1) {
      const orbit = index / 14;
      const x = this.width * orbit;
      const y = this.height * (0.2 + 0.08 * Math.sin(time * 0.6 + index));
      this.context.fillStyle = "rgba(255, 255, 255, 0.035)";
      this.context.beginPath();
      this.context.arc(x, y, 2 + ((index + 1) % 3), 0, Math.PI * 2);
      this.context.fill();
    }
  }

  drawGrid(time) {
    this.context.save();
    this.context.strokeStyle = "rgba(255, 255, 255, 0.05)";
    this.context.lineWidth = 1;
    const driftX = (this.pointer.x - 0.5) * 14;
    const driftY = (this.pointer.y - 0.5) * 12;

    for (let x = -GRID_SPACING; x < this.width + GRID_SPACING; x += GRID_SPACING) {
      const animatedX = x + driftX + Math.sin(time * 0.2 + x * 0.01) * 4;
      this.context.beginPath();
      this.context.moveTo(animatedX, 0);
      this.context.lineTo(animatedX, this.height);
      this.context.stroke();
    }

    for (let y = -GRID_SPACING; y < this.height + GRID_SPACING; y += GRID_SPACING) {
      const animatedY = y + driftY + Math.cos(time * 0.18 + y * 0.01) * 4;
      this.context.beginPath();
      this.context.moveTo(0, animatedY);
      this.context.lineTo(this.width, animatedY);
      this.context.stroke();
    }

    this.context.restore();
  }

  drawNodes(time) {
    if (this.nodes.length === 0) {
      return;
    }

    this.context.save();
    this.context.textAlign = "left";
    this.context.textBaseline = "middle";
    this.context.font = '600 14px "Avenir Next", "Gill Sans", sans-serif';

    for (const node of this.nodes) {
      const wave = Math.sin(time * 0.95 + node.phase) * 0.012;
      const x = this.width * clamp(node.x + wave + (this.pointer.x - 0.5) * 0.03, 0.08, 0.92);
      const y = this.height * clamp(node.y - wave + (this.pointer.y - 0.5) * 0.02, 0.08, 0.92);
      const radius = Math.min(this.width, this.height) * node.radius;

      this.context.fillStyle = hexToRgba(node.accent_color, 0.22);
      this.context.beginPath();
      this.context.arc(x, y, radius * 1.65, 0, Math.PI * 2);
      this.context.fill();

      this.context.fillStyle = node.accent_color;
      this.context.beginPath();
      this.context.arc(x, y, radius, 0, Math.PI * 2);
      this.context.fill();

      this.context.strokeStyle = "rgba(255, 255, 255, 0.16)";
      this.context.beginPath();
      this.context.arc(x, y, radius * 1.2, 0, Math.PI * 2);
      this.context.stroke();

      this.context.fillStyle = "rgba(248, 242, 231, 0.95)";
      this.context.fillText(node.label, x + radius + 14, y - 6);

      this.context.fillStyle = "rgba(180, 192, 206, 0.9)";
      this.context.font = '400 12px "Avenir Next", "Gill Sans", sans-serif';
      this.context.fillText(node.slug, x + radius + 14, y + 13);
      this.context.font = '600 14px "Avenir Next", "Gill Sans", sans-serif';
    }

    this.context.restore();
  }

  drawRipples(delta) {
    if (this.ripples.length === 0) {
      return;
    }

    this.context.save();

    this.ripples = this.ripples.filter((ripple) => ripple.life < 1);
    for (const ripple of this.ripples) {
      ripple.life += delta * 0.9;
      const radius = Math.min(this.width, this.height) * (0.04 + ripple.life * 0.22);
      this.context.strokeStyle = hexToRgba(ripple.color, 0.65 * (1 - ripple.life));
      this.context.lineWidth = 2;
      this.context.beginPath();
      this.context.arc(this.width * ripple.x, this.height * ripple.y, radius, 0, Math.PI * 2);
      this.context.stroke();
    }

    this.context.restore();
  }
}

