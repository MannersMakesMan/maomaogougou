<template>
	<!-- #ifndef MP-WEIXIN  -->
	<!-- && !screenShot -->
	<view class="cu-modal" v-if="showLogin" :class="[{ show: showLogin }, modalType]" cathctouchmove >
		<view class="cu-dialog" @tap.stop style="background: none;overflow: visible;">
			<view class="modal-box">
				<image class="head-bg" src="./modal.png" mode=""></image>
				<view class="detail">
					<view class="title1">您还没有登录</view>
					<view class="title2">登录即刻开启品质生活</view>
				</view>
				<view class="btn-box y-f">
					<button class="cu-btn login-btn" @tap="onLogin">立即登录</button>
					<button class="cu-btn close-btn" @tap="hideModal">取消</button>
				</view>
			</view>
		</view>
	</view>
	<!-- #endif  -->
	<!-- #ifdef MP-WEIXIN  -->
	<!-- forceOauth || -->
	<view class="force-login-wrap" v-if="showLogin">
		<view class="force-login__content y-f">
			<open-data class="user-avatar" type="userAvatarUrl"></open-data>
			<open-data class="user-name" type="userNickName"></open-data>
			<view class="login-notice">为了提供更优质的服务，需要获取您的头像昵称</view>
			<button class="cu-btn author-btn" @getuserinfo="appLoginWx" open-type="getUserInfo">授权并查看</button>
			<button class="cu-btn close-btn" @tap="closeAuth">暂不授权</button>
		</view>
	</view>
	<!-- #endif  -->
</template>

<script>
// import Wechat from '@/common/wechat/wechat';
import { mapMutations, mapActions, mapState } from 'vuex';
export default {
	name: 'shoproLoginModal',
	components: {},
	data() {
		return {
			appId: 'wx35843fee2b2f4e35',
			appSecret:'b705463a8ed0727df4d031c4f71191a3',
			js_code:'',
			grant_type:'authorization_code',
		};
	},
	props: {
		value: {},
		modalType: {
			type: String,
			default: ''
		}
	},
	onLoad() {
		console.log('我的');
	},
	computed: {
		...mapState({
			showLoginTip: state => state.login.showLoginTip
		}),
		showLogin: {
			get() {
				return this.showLoginTip;
			},
			set(val) {
				console.log(val, '-=');
				this.$store.commit('LOGIN_TIP', val);
			}
		}
	},
	methods: {
		// ...mapActions(['setTokenAndBack']),

		// 隐藏登录弹窗
		hideModal() {
			this.showLogin = false;
			uni.switchTab({
				url:'/pages/index/index'
			})
		},

		// 去登录
		onLogin() {
			this.showLogin = false;
			uni.redirectTo({
				url:'../../pages/Login/Login'
			})
		},

		// 小程序，获取用户信息登录
		async getuserinfo(e) {
			var wechat = new Wechat();
			let token = await wechat.wxMiniProgramLogin(e);
			this.$store.commit('FORCE_OAUTH', false);
			this.$store.commit('LOGIN_TIP', false);
			uni.setStorageSync('fromLogin', this.$Route);
			this.setTokenAndBack(token);
		},
	// 小程序，用户授权
		appLoginWx(){
			// #ifdef MP-WEIXIN
				uni.getProvider({
				  service: 'oauth',
				  success: function (res) {
					if (~res.provider.indexOf('weixin')) {
						uni.login({
							provider: 'weixin',
							success: (res2) => {
								uni.getUserInfo({
									provider: 'weixin',
									success: (info) => {//这里请求接口
									debugger
										console.log(res);
										console.log(res2);
										console.log(info);
										
									},
									fail: () => {
										uni.showToast({title:"微信登录授权失败",icon:"none"});
									}
								})
						
							},
							fail: () => {
								uni.showToast({title:"微信登录授权失败",icon:"none"});
							}
						})
						
					}else{
						uni.showToast({
							title: '请先安装微信或升级版本',
							icon:"none"
						});
					}
				  }
				});
				//#endif
		},
		// 小程序，取消登录
		closeAuth() {
			this.$store.commit('LOGIN_TIP', false);
		}
	}
};
</script>

<style lang="scss">
// 登录提示
.modal-box {
	width: 610rpx;
	border-radius: 20rpx;
	background: #fff;
	position: relative;
	left: 50%;
	transform: translateX(-50%);
	padding-bottom: 30rpx;

	.head-bg {
		width: 100%;
		height: 210rpx;
	}

	.detail {
		.title1 {
			color: #46351b;
			font-size: 35rpx;
			font-weight: bold;
		}

		.title2 {
			font-size: 28rpx;
			color: #999;
			padding-top: 20rpx;
		}
	}

	.btn-box {
		margin-top: 80rpx;

		.login-btn {
			width: 492rpx;
			height: 70rpx;
			background: linear-gradient(90deg, #2676fc, #2676fc);
			box-shadow: 0px 7rpx 6rpx 0px #c5dafe;
			border-radius: 35rpx;
			font-size: 28rpx;
			color: rgba(#fff, 0.9);
		}

		.close-btn {
			width: 492rpx;
			height: 70rpx;
			color: #333;
			font-size: 26rpx;
			margin-top: 20rpx;
			background: none;
		}
	}
}

// 小程序登录提醒
/* #ifdef MP-WEIXIN */
.force-login-wrap {
	position: fixed;
	width: 100vw;
	height: 100vh;
	overflow: hidden;
	z-index: 11111;
	top: 0;
	background: url(./modal.png) #fff no-repeat;
	background-size: 100% 100%;
	// background: linear-gradient(180deg, rgba(239, 196, 128, 1) 0%, rgba(248, 220, 165, 1) 25%, rgba(255, 255, 255, 1) 98%);

	.logo-bg {
		width: 640rpx;
		height: 300rpx;
	}

	.force-login__content {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);

		.user-avatar {
			width: 160rpx;
			height: 160rpx;
			border-radius: 50%;
			overflow: hidden;
			margin-bottom: 40rpx;
		}

		.user-name {
			font-size: 35rpx;
			font-family: PingFang SC;
			font-weight: bold;
			color: #333333;
			margin-bottom: 30rpx;
		}

		.login-notice {
			font-size: 28rpx;
			font-family: PingFang SC;
			font-weight: 400;
			color: #2676fc;
			line-height: 44rpx;
			width: 400rpx;
			text-align: center;
			margin-bottom: 80rpx;
		}

		.author-btn {
			width: 630rpx;
			height: 80rpx;
			background: linear-gradient(90deg, #2676fc, #2676fc);
			box-shadow: 0px 7rpx 6rpx 0px #d3e3ff;
			border-radius: 40rpx;
			font-size: 30rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: rgba(255, 255, 255, 1);
		}

		.close-btn {
			width: 630rpx;
			height: 80rpx;
			margin-top: 30rpx;
			border-radius: 40rpx;
			border: 2rpx solid #2676fc;
			background: none;
			font-size: 30rpx;
			font-family: PingFang SC;
			font-weight: 500;
			color: #2676fc;
		}
	}
}

/* #endif */
</style>
