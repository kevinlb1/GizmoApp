const GRID_SIZE = 44;


function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}


function createCanvasTexture(size = 256) {
  const texture = document.createElement("canvas");
  texture.width = size;
  texture.height = size;
  const context = texture.getContext("2d");
  const image = context.createImageData(size, size);

  for (let index = 0; index < image.data.length; index += 4) {
    const pixel = index / 4;
    const x = pixel % size;
    const y = Math.floor(pixel / size);
    const wave = Math.sin(x * 0.07) * 8 + Math.cos(y * 0.05) * 8;
    const shade = 242 + wave + ((x * y) % 11);
    image.data[index] = shade;
    image.data[index + 1] = Math.min(255, shade + 5);
    image.data[index + 2] = Math.max(220, shade - 8);
    image.data[index + 3] = 255;
  }

  context.putImageData(image, 0, 0);
  return texture;
}


export class SceneRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.context = canvas.getContext("2d");
    this.pointer = { x: 0.5, y: 0.5, active: false };
    this.ripples = [];
    this.sprites = [];
    this.nodes = [];
    this.textures = new Map([["paper", createCanvasTexture()]]);
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

  setNodes(nodes) {
    this.nodes = Array.isArray(nodes) ? nodes : [];
  }

  async loadTexture(name, url) {
    const image = new Image();
    image.decoding = "async";
    image.src = url;
    await image.decode();
    this.textures.set(name, image);
    return image;
  }

  addSprite(sprite) {
    this.sprites.push({
      texture: "paper",
      x: 0.5,
      y: 0.5,
      width: 120,
      height: 120,
      opacity: 1,
      rotation: 0,
      ...sprite,
    });
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
    this.drawNodeSprites(timestamp);
    this.drawSprites();
    this.drawRipples(delta);

    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  drawBackdrop() {
    const texture = this.textures.get("paper");
    const pattern = this.context.createPattern(texture, "repeat");
    this.context.fillStyle = pattern || "#fbfcf8";
    this.context.fillRect(0, 0, this.width, this.height);

    const gradient = this.context.createLinearGradient(0, 0, this.width, this.height);
    gradient.addColorStop(0, "rgba(18, 118, 111, 0.14)");
    gradient.addColorStop(0.5, "rgba(255, 255, 255, 0.2)");
    gradient.addColorStop(1, "rgba(184, 95, 58, 0.12)");
    this.context.fillStyle = gradient;
    this.context.fillRect(0, 0, this.width, this.height);
  }

  drawGrid() {
    this.context.save();
    this.context.strokeStyle = "rgba(39, 49, 43, 0.09)";
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

  drawNodeSprites(timestamp) {
    if (this.nodes.length === 0) {
      return;
    }

    this.context.save();
    for (const node of this.nodes) {
      const pulse = Math.sin(timestamp * 0.0015 + node.id) * 0.05;
      const radius = Math.min(this.width, this.height) * (node.radius + pulse);
      const x = this.width * node.x;
      const y = this.height * node.y;
      const gradient = this.context.createRadialGradient(x, y, radius * 0.18, x, y, radius);
      gradient.addColorStop(0, node.accent_color);
      gradient.addColorStop(0.72, `${node.accent_color}cc`);
      gradient.addColorStop(1, `${node.accent_color}00`);

      this.context.globalCompositeOperation = "multiply";
      this.context.fillStyle = gradient;
      this.context.fillRect(x - radius, y - radius, radius * 2, radius * 2);
    }
    this.context.restore();
  }

  drawSprites() {
    if (this.sprites.length === 0) {
      return;
    }

    this.context.save();
    for (const sprite of this.sprites) {
      const texture = this.textures.get(sprite.texture);
      if (!texture) {
        continue;
      }
      const x = this.width * sprite.x;
      const y = this.height * sprite.y;
      this.context.save();
      this.context.translate(x, y);
      this.context.rotate(sprite.rotation);
      this.context.globalAlpha = sprite.opacity;
      this.context.drawImage(texture, -sprite.width / 2, -sprite.height / 2, sprite.width, sprite.height);
      this.context.restore();
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
      this.context.strokeStyle = `rgba(18, 118, 111, ${0.42 * (1 - ripple.life)})`;
      this.context.lineWidth = 2;
      this.context.beginPath();
      this.context.arc(this.width * ripple.x, this.height * ripple.y, radius, 0, Math.PI * 2);
      this.context.stroke();
    }

    this.context.restore();
  }
}
