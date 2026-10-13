'use strict';

// Original paper frames are readable as a contact sheet without JavaScript.
document.querySelectorAll('[data-sequence]').forEach(sequence => {
  const frames = [...sequence.querySelectorAll('.sequence-stage figure')];
  const play = sequence.querySelector('.sequence-play');
  const thumbnails = sequence.querySelector('.sequence-thumbnails');
  let index = 0;
  let timer;
  let playing = false;

  function stop() {
    clearTimeout(timer);
    playing = false;
    play.textContent = index === frames.length - 1 ? 'Replay frames' : 'Play frames';
    play.setAttribute('aria-pressed', 'false');
  }

  function show(next) {
    index = next;
    frames.forEach((frame, i) => frame.toggleAttribute('data-active', i === index));
    [...thumbnails.children].forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
  }

  function advance() {
    timer = setTimeout(() => {
      if (index === frames.length - 1) {
        stop();
        return;
      }
      show(index + 1);
      advance();
    }, 1600);
  }

  frames.forEach((frame, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.setAttribute('aria-label', `Show frame ${i + 1} of ${frames.length}`);
    const image = frame.querySelector('img').cloneNode();
    image.alt = '';
    button.append(image);
    button.addEventListener('click', () => { show(i); stop(); });
    thumbnails.append(button);
  });
  play.addEventListener('click', () => {
    if (playing) { stop(); return; }
    if (index === frames.length - 1) show(0);
    playing = true;
    play.textContent = 'Pause frames';
    play.setAttribute('aria-pressed', 'true');
    advance();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) stop();
  }).observe(sequence);
  window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', stop);
  show(0);
  sequence.classList.add('sequence-ready');
  sequence.querySelector('.sequence-toolbar').hidden = false;
  thumbnails.hidden = false;
});

// Link task descriptions to the existing four-policy comparison without starting playback.
document.querySelectorAll('[data-compare-task]').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelector(`[data-task="${link.dataset.compareTask}"]`).click();
  });
});

document.querySelectorAll('[data-result-view-target]').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelector(`[data-results-view="${link.dataset.resultViewTarget}"]`).click();
  });
});
