<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import '@/static/style/index.css';
	@import 'static/style/icon.css';
	@import 'static/font/shopro-icon.css';

	page {
		-webkit-overflow-scrolling: touch; //ios滑动不流畅
		height: 100%;
		background: #f6f6f6;
		width: 100%;
		font-size: 30upx;
		font-family: NotoSansHans-Bold;
		word-break: break-all; //英文文本不换行
		color: #333;
	}

	::-webkit-scrollbar {
		width: 0;
		height: 0;
		color: transparent;
		display: none;
	}
</style>
