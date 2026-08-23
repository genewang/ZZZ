Page({
  data: {
    src: "/media/flywheel-layers-soothing.mp4",
    playing: false,
  },

  onPlay() {
    this.setData({ playing: true });
  },

  onPause() {
    this.setData({ playing: false });
  },

  onEnded() {
    this.setData({ playing: false });
  },

  replay() {
    const ctx = wx.createVideoContext("flywheelVideo", this);
    ctx.seek(0);
    ctx.play();
  },
});
