export async function createAudioRecorder({ onSamples, sampleWindow = 2048 } = {}) {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const context = new AudioContext();
  const source = context.createMediaStreamSource(stream);
  const analyser = context.createAnalyser();
  analyser.fftSize = sampleWindow;
  source.connect(analyser);

  const samples = new Float32Array(analyser.fftSize);

  function readSamples() {
    analyser.getFloatTimeDomainData(samples);
    if (onSamples) {
      onSamples(Array.from(samples), context.sampleRate);
    }
  }

  function stop() {
    stream.getTracks().forEach((track) => track.stop());
    context.close();
  }

  return { readSamples, stop, sampleRate: context.sampleRate };
}
