<template>
	<view class="">
		<view class="container" v-if="!showLoginTip">
			<view class="user-list x-bc">
				<text class="list-name">用户名</text>
				<view class="x-f">
					<input class="list-val" v-model="userInfo.name" disabled="true" />
					<!-- <text class="iconfont icon-chevron-right cuIcon-right"></text> -->
				</view>
			</view>
			<!-- <picker style="width: 750rpx;" mode="selector" :value="index" :range="labelArray" :range-key="'name'" @change="onDateChange"> -->
			<view class="user-list x-bc">
				<text class="list-name">头像</text>
				<view class="x-f">
					<!-- <input class="list-val" v-model="userInfo.name" disabled="true" /> -->
					<image :src="userInfo.avatar" style="width: 50rpx;height: 50rpx;" mode=""></image>
					<!-- <text class="iconfont icon-chevron-right cuIcon-right"></text> -->
				</view>
			</view>
			<!-- </picker> -->

			<!-- <view class="btn-box flex align-center justify-center"><button class="cu-btn confirem-btn" @tap="confirmUserInfo">保存</button></view> -->
			<view class="btn-box flex align-center justify-center"><button class="cu-btn confirem-btn"
					@tap="editUserInfo">退出登录</button></view>
		</view>
		<!-- 登录提示 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import {
		mapMutations,
		mapActions,
		mapState
	} from 'vuex';
	import {
		logout
	} from '@/api/modules/login.js'

	export default {
		data() {
			return {
				labelArray: [{
						name: '男',
						id: 1
					},
					{
						name: "女",
						id: 2
					}
				],
				index: 0,
				show1: false,
				newPassword: "",
				oldPassword: "",
				status: false
			};
		},
		computed: {
			...mapState({
				showLoginTip: state => state.login.showLoginTip,
				userInfo: state => state.login.userInfo
			}),
		},
		onLoad() {
			if (!this.showLoginTip && JSON.stringify(this.userInfo) != '{}') {

			} else {
				this.$store.commit('LOGIN_TIP', true)
			}

		},
		methods: {
			// 退出登录
			editUserInfo() {
				uni.showModal({
					title: '提示',
					content: '是否选择退出登录?',
					success: (res) => {
						if (res.confirm) {
							logout().then(res => {
								if (res.code == '200') {
									uni.removeStorageSync('token');
									uni.removeStorageSync('userInfo');
									this.$store.commit('USER_INFO', {});
									this.$store.commit('VIP_INFO', {});
									uni.redirectTo({
										url: '/pages/Login/Login'
									})
								}
							})

						} else if (res.cancel) {
							console.log('用户点击取消');
						}
					}
				});
			},
		}
	};
</script>

<style lang="scss">
	.input-name,
	.input-password {
		height: 80upx;
		width: 100%;
		display: flex;
		flex-direction: row;
		justify-content: center;
		align-items: center;
		position: relative;
		padding-left: 30upx;
		box-sizing: border-box;
	}

	.input-name::after {
		content: " ";
		position: absolute;
		left: 30upx;
		bottom: 0;
		right: 0;
		height: 1px;
		border-top: 1px solid #e5e5e5;
		transform-origin: 0 0;
		transform: scaleY(.5);
	}

	.input-name view,
	.input-password view {
		width: 120upx;
		height: 50upx;
		line-height: 50upx;
		font-size: 28upx;
		color: #333333;
	}

	.input-name input,
	.input-password input {
		flex: 1;
		height: 50upx;
		line-height: 50upx;
	}

	.user-list {
		background: #fff;
		height: 100rpx;
		border-bottom: 1rpx solid #f6f6f6;
		padding: 0 20rpx;

		.list-name {
			font-size: 28rpx;
		}

		.avatar {
			width: 67rpx;
			height: 67rpx;
			border-radius: 50%;
			// background: #ccc;
		}

		.cuIcon-right {
			margin-left: 25rpx;
		}

		.list-val {
			color: #999;
			font-size: 28rpxc;
			text-align: right;
		}
	}

	.btn-box {
		margin-top: 60rpx;

		.confirem-btn {
			width: 710rpx;
			height: 80rpx;
			background: linear-gradient(90deg, #2676FC, #2676FC);
			border: 1rpx solid rgba(238, 238, 238, 1);
			border-radius: 40rpx;
			font-size: 30rpx;
			color: rgba(#fff, 0.9);
		}
	}
</style>
