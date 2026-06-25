const GRID_SIZE = 44;
const SPRITE_TEXTURE_SIZE = 160;


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


function hexToRgb(hexColor) {
  const normalized = String(hexColor || "#12766f").replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(normalized)) {
    return { red: 18, green: 118, blue: 111 };
  }
  return {
    red: Number.parseInt(normalized.slice(0, 2), 16),
    green: Number.parseInt(normalized.slice(2, 4), 16),
    blue: Number.parseInt(normalized.slice(4, 6), 16),
  };
}


function createSpriteTexture(accentColor, size = SPRITE_TEXTURE_SIZE) {
  const texture = document.createElement("canvas");
  texture.width = size;
  texture.height = size;
  const context = texture.getContext("2d");
  const { red, green, blue } = hexToRgb(accentColor);
  const center = size / 2;
  const radius = size * 0.42;

  const glow = context.createRadialGradient(center, center, size * 0.1, center, center, radius);
  glow.addColorStop(0, `rgba(${red}, ${green}, ${blue}, 0.95)`);
  glow.addColorStop(0.56, `rgba(${red}, ${green}, ${blue}, 0.62)`);
  glow.addColorStop(1, `rgba(${red}, ${green}, ${blue}, 0)`);
  context.fillStyle = glow;
  context.fillRect(0, 0, size, size);

  const image = context.getImageData(0, 0, size, size);
  for (let index = 0; index < image.data.length; index += 4) {
    const pixel = index / 4;
    const x = pixel % size;
    const y = Math.floor(pixel / size);
    const dx = x - center;
    const dy = y - center;
    const distance = Math.sqrt(dx * dx + dy * dy) / radius;
    if (distance > 1) {
      continue;
    }

    const grain = Math.sin(x * 0.22) * 10 + Math.cos(y * 0.17) * 10 + ((x * 13 + y * 7) % 17);
    const edge = Math.max(0, 1 - distance);
    image.data[index] = clamp(image.data[index] + grain * edge, 0, 255);
    image.data[index + 1] = clamp(image.data[index + 1] + grain * edge, 0, 255);
    image.data[index + 2] = clamp(image.data[index + 2] + grain * edge, 0, 255);
    image.data[index + 3] = clamp(image.data[index + 3] + 18 * edge, 0, 255);
  }
  context.putImageData(image, 0, 0);

  context.save();
  context.globalCompositeOperation = "screen";
  context.beginPath();
  context.ellipse(size * 0.42, size * 0.34, size * 0.12, size * 0.06, -0.45, 0, Math.PI * 2);
  context.fillStyle = "rgba(255, 255, 255, 0.55)";
  context.fill();
  context.restore();

  return texture;
}


export class SceneRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.context = canvas.getContext("2d");
    this.pointer = { x: 0.5, y: 0.5, active: false };
    this.ripples = [];
    this.sprites = [];
    this.nodeSprites = [];
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
    this.drawFrame(performance.now(), 0);
    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = Math.floor(rect.width * this.pixelRatio);
    this.canvas.height = Math.floor(rect.height * this.pixelRatio);
    this.context.setTransform(this.pixelRatio, 0, 0, this.pixelRatio, 0, 0);
    this.drawFrame(performance.now(), 0);
  }

  destroy() {
    window.cancelAnimationFrame(this.animationFrame);
    this.resizeObserver.disconnect();
    this.canvas.removeEventListener("pointermove", this.handlePointerMove);
    this.canvas.removeEventListener("pointerdown", this.handlePointerDown);
    this.canvas.removeEventListener("pointerleave", this.handlePointerLeave);
  }

  setNodes(nodes) {
    this.nodeSprites = Array.isArray(nodes)
      ? nodes.map((node) => this.createNodeSprite(node))
      : [];
    this.canvas.dataset.spriteCount = String(this.nodeSprites.length);
    this.drawFrame(performance.now(), 0);
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
    this.drawFrame(performance.now(), 0);
  }

  createNodeSprite(node) {
    const textureName = `node-${node.slug || node.id}`;
    if (!this.textures.has(textureName)) {
      this.textures.set(textureName, createSpriteTexture(node.accent_color));
    }

    return {
      texture: textureName,
      x: node.x,
      y: node.y,
      width: Math.max(96, 760 * node.radius),
      height: Math.max(96, 760 * node.radius),
      opacity: 0.92,
      rotation: 0,
      pulseSeed: Number(node.id || 0),
    };
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

    this.drawFrame(timestamp, delta);

    this.animationFrame = window.requestAnimationFrame(this.render);
  }

  drawFrame(timestamp, delta) {
    if (!this.width || !this.height) {
      return;
    }

    this.drawBackdrop();
    this.drawGrid();
    this.drawNodeSprites(timestamp);
    this.drawSprites();
    this.drawRipples(delta);
    this.canvas.dataset.rendered = "true";
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
    if (this.nodeSprites.length === 0) {
      return;
    }

    this.context.save();
    this.context.globalCompositeOperation = "multiply";
    for (const sprite of this.nodeSprites) {
      const pulse = 1 + Math.sin(timestamp * 0.0015 + sprite.pulseSeed) * 0.04;
      this.drawSprite({ ...sprite, width: sprite.width * pulse, height: sprite.height * pulse });
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
      this.drawSprite(sprite);
    }
    this.context.restore();
  }

  drawSprite(sprite) {
    const texture = this.textures.get(sprite.texture);
    if (!texture) {
      return;
    }
    const x = this.width * sprite.x;
    const y = this.height * sprite.y;
    this.context.save();
    this.context.translate(x, y);
    this.context.rotate(sprite.rotation || 0);
    this.context.globalAlpha = sprite.opacity ?? 1;
    this.context.drawImage(texture, -sprite.width / 2, -sprite.height / 2, sprite.width, sprite.height);
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
