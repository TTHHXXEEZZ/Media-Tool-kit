const { createApp } = Vue;
const { createVuetify } = Vuetify;
const vuetify = createVuetify({
    theme: { defaultTheme: 'light', colors: { primary: '#10B981', emerald: '#10B981' } }
});

createApp({
    data() {
        return {
            drawerLeft: true,
            loading: false,
            editorLoading: false,
            activeTab: 'convert',

            // ข้อมูลไฟล์และฟอร์แมต
            files: null,
            convertFormat: 'PNG',
            compressType: 'image',

            // ข้อมูลดาวน์โหลดวิดีโอ
            videoUrl: '',
            downloadQuality: 'best',
            videoInfo: { title: '', thumbnail: '', duration: '', qualities: [] },
            qualityOptions: [
                { text: 'Best (Auto)', value: 'best' },
                { text: 'Audio Only', value: 'audio' }
            ],

            // พรีวิวไฟล์
            previewUrl: null,
            previewType: 'image',

            // สถานะเครื่องมือแต่งรูป
            paintColor: '#000000',
            brushSize: 5,
            isErasing: false,
            isCropping: false,
            cropper: null,
            isDrawing: false,
            watermarkText: '',

            // กล่องแจ้งเตือน
            snackbar: { show: false, text: '', color: 'success' },

            // ตัวหน่วงเวลาดึงข้อมูล
            debounceFetchInfo: null
        };
    },

    mounted() {
        if (window.innerWidth < 960) this.drawerLeft = false;
        this.debounceFetchInfo = _.debounce(this.fetchVideoInfo, 1000);
    },

    methods: {
        notify(text, color = 'success') {
            this.snackbar = { show: true, text, color };
        },

        getTitle(tab) {
            return {
                convert: 'Converter',
                basic: 'Basic Editor',
                frames: 'Frames',
                download: 'Downloader',
                editor: 'AI Studio',
                compress: 'Compressor',
                audio: 'Audio'
            }[tab] || 'Workspace';
        },

        switchTab(tab) {
            this.activeTab = tab;
            this.resetPreview();
        },

        resetPreview() {
            this.files = null;
            this.previewUrl = null;
            this.videoUrl = '';
            if (this.cropper) { this.cropper.destroy(); this.cropper = null; }
            this.isCropping = false;
            this.watermarkText = '';
        },

        handlePreview(files) {
            if (!files || !files.length) { this.previewUrl = null; return; }
            this.previewUrl = URL.createObjectURL(files[0]);
            this.previewType = files[0].type.startsWith('video') ? 'video' : 'image';
        },

        // ฟังก์ชันแต่งรูปพื้นฐาน
        initCanvas(files) {
            if (!files || !files.length) return;
            this.handlePreview(files);
            const file = files[0];
            const img = new Image();
            img.src = URL.createObjectURL(file);
            img.onload = () => {
                const canvas = this.$refs.paintCanvas;
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const MAX_W = 1000;
                let w = img.width, h = img.height;
                if (w > MAX_W) { h = h * (MAX_W / w); w = MAX_W; }
                canvas.width = w;
                canvas.height = h;
                ctx.drawImage(img, 0, 0, w, h);
            };
        },

        startPainting(e) { this.isDrawing = true; this.draw(e); },
        stopPainting() {
            this.isDrawing = false;
            const c = this.$refs.paintCanvas;
            if (c) c.getContext('2d').beginPath();
        },
        draw(e) {
            if (!this.isDrawing) return;
            const canvas = this.$refs.paintCanvas;
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            ctx.lineWidth = this.brushSize;
            ctx.lineCap = 'round';
            ctx.strokeStyle = this.isErasing ? '#FFFFFF' : this.paintColor;
            ctx.lineTo((e.clientX - rect.left) * scaleX, (e.clientY - rect.top) * scaleY);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo((e.clientX - rect.left) * scaleX, (e.clientY - rect.top) * scaleY);
        },

        toggleCropMode() {
            this.editorLoading = true;
            setTimeout(() => {
                this.isCropping = !this.isCropping;
                if (this.isCropping) {
                    const canvas = this.$refs.paintCanvas;
                    const cropImg = this.$refs.cropImage;
                    cropImg.src = canvas.toDataURL('image/jpeg', 0.8);
                    this.$nextTick(() => {
                        if (this.cropper) this.cropper.destroy();
                        this.cropper = new Cropper(cropImg, { viewMode: 1, autoCropArea: 0.8 });
                        this.editorLoading = false;
                    });
                } else {
                    if (this.cropper) {
                        const croppedCanvas = this.cropper.getCroppedCanvas();
                        const canvas = this.$refs.paintCanvas;
                        const ctx = canvas.getContext('2d');
                        canvas.width = croppedCanvas.width;
                        canvas.height = croppedCanvas.height;
                        ctx.drawImage(croppedCanvas, 0, 0);
                        this.cropper.destroy();
                        this.cropper = null;
                    }
                    this.editorLoading = false;
                }
            }, 50);
        },

        rotateImg(deg) { this.editCanvasOp('rotate', deg); },
        flipImg(dir) { this.editCanvasOp('flip', dir); },

        editCanvasOp(op, val) {
            const canvas = this.$refs.paintCanvas;
            const ctx = canvas.getContext('2d');
            const temp = document.createElement('canvas');
            temp.width = canvas.width;
            temp.height = canvas.height;
            temp.getContext('2d').drawImage(canvas, 0, 0);
            if (op === 'rotate' && Math.abs(val) === 90) {
                canvas.width = temp.height;
                canvas.height = temp.width;
            }
            ctx.save();
            if (op === 'rotate') {
                ctx.translate(canvas.width / 2, canvas.height / 2);
                ctx.rotate(val * Math.PI / 180);
                ctx.drawImage(temp, -temp.width / 2, -temp.height / 2);
            } else if (op === 'flip') {
                if (val === 'h') { ctx.scale(-1, 1); ctx.drawImage(temp, -canvas.width, 0); }
                else { ctx.scale(1, -1); ctx.drawImage(temp, 0, -canvas.height); }
            }
            ctx.restore();
        },

        addTextToCanvas() {
            if (!this.watermarkText) return;
            const canvas = this.$refs.paintCanvas;
            const ctx = canvas.getContext('2d');
            const fontSize = Math.max(20, canvas.width * 0.05);
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.fillStyle = this.paintColor;
            ctx.fillText(this.watermarkText, 50, 50 + fontSize);
            this.watermarkText = '';
        },

        saveCanvas() {
            this.loading = true;
            this.$refs.paintCanvas.toBlob(async (blob) => {
                const fd = new FormData();
                fd.append('file', blob, 'edited.png');
                fd.append('format', 'PNG');
                try {
                    const res = await axios.post('/api/process/convert', fd);
                    window.open(res.data.url, '_blank');
                } catch (e) {
                    this.notify('Save failed', 'error');
                } finally {
                    this.loading = false;
                }
            });
        },

        // ฟังก์ชันดาวน์โหลดวิดีโอ
        async fetchVideoInfo() {
            if (!this.videoUrl) return;
            try {
                const res = await axios.post('/api/process/info', { url: this.videoUrl });
                const info = res.data;
                this.videoInfo = { ...info };
                this.qualityOptions = [
                    { text: 'Best', value: 'best' },
                    ...info.qualities.map(q => ({ text: `${q}p`, value: q })),
                    { text: 'Audio Only', value: 'audio' }
                ];
            } catch (e) {
                // ข้าม error ตอนพิมพ์ URL ยังไม่เสร็จ
            }
        },

        async downloadVideo() {
            this.loading = true;
            try {
                const res = await axios.post('/api/process/download', {
                    url: this.videoUrl,
                    quality: this.downloadQuality
                });
                window.open(res.data.url, '_blank');
            } catch (e) {
                this.notify('Download failed', 'error');
            } finally {
                this.loading = false;
            }
        },

        // ฟังก์ชันอัปโหลดไฟล์ประมวลผลทั่วไป
        async upload(action, extra = {}) {
            this.loading = true;
            const fd = new FormData();
            fd.append('file', this.files[0]);
            for (const k in extra) fd.append(k, extra[k]);
            try {
                const res = await axios.post(`/api/process/${action}`, fd);
                window.open(res.data.url, '_blank');
            } catch (e) {
                this.notify('Processing failed', 'error');
            } finally {
                this.loading = false;
            }
        }
    }
}).use(vuetify).mount('#app');
