const GRID_SIZE = 40;


function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}


export class SceneRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.context = canvas.getContext("2d");
    this.pointer = { x: 0.5, y: 0.5, active: false };
    this.ripples = [];
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
    this.ripples.push({
      x: this.pointer.x,
      y: this.pointer.y,
      life: 0,
    });
  }

  handlePointerLeave() {
    this.pointer.active = false;
  }

  render(timestamp) {
    const delta = Math.min(0.033, (timestamp - this.lastTimestamp) * 0.001 || 0.016);
    this.lastTimestamp = timestamp;

    this.drawBackdrop();
    this.drawGrid();
    this.drawRipples(delta);

    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  drawBackdrop() {
    const gradient = this.context.createLinearGradient(0, 0, this.width, this.height);
    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(1, "#eef7ff");
    this.context.fillStyle = gradient;
    this.context.fillRect(0, 0, this.width, this.height);
  }

  drawGrid() {
    this.context.save();
    this.context.strokeStyle = "rgba(94, 125, 155, 0.12)";
    this.context.lineWidth = 1;

    for (let x = GRID_SIZE; x < this.width; x += GRID_SIZE) {
      this.context.beginPath();
      this.context.moveTo(x, 0);
      this.context.lineTo(x, this.height);
      this.context.stroke();
    }

    for (let y = GRID_SIZE; y < this.height; y += GRID_SIZE) {
      this.context.beginPath();
      this.context.moveTo(0, y);
      this.context.lineTo(this.width, y);
      this.context.stroke();
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
      ripple.life += delta * 1.1;
      const radius = Math.min(this.width, this.height) * (0.03 + ripple.life * 0.18);
      this.context.strokeStyle = `rgba(40, 127, 133, ${0.42 * (1 - ripple.life)})`;
      this.context.lineWidth = 2;
      this.context.beginPath();
      this.context.arc(this.width * ripple.x, this.height * ripple.y, radius, 0, Math.PI * 2);
      this.context.stroke();
    }

    this.context.restore();
  }
}
