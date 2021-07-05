<template>
	<view style="background-color: #F5F5F5;">
		<view class="header-bg">
			<view class="userInfo">
				<image :src="userInfo.avatar" mode="" style="width: 110rpx;height: 110rpx;border-radius: 50%;"></image>
				<view class="" style="padding-left: 30rpx;">
					<view class="userInfo-name">
						{{userInfo.name}}
					</view>
				</view>
			</view>
		</view>
		<!-- 菜单 -->
		<view class="tab-list">
			<tui-list-view>
				<tui-list-cell :arrow="true" @click="onClickPath">
					<view class="tui-item-box">
						<image src="../../static/kehu.jpg" mode="" style="width: 48rpx;height: 48rpx;"></image>
						<text class="tui-list-cell_name">客户管理</text>
					</view>
				</tui-list-cell>
				<tui-list-cell :arrow="true" @click="onClickPathOrder">
					<view class="tui-item-box">
						<image src="../../static/order.png" mode="" style="width: 48rpx;height: 48rpx;"></image>
						<text class="tui-list-cell_name">订单管理</text>
					</view>
				</tui-list-cell>
				<tui-list-cell :arrow="true" @click="onClickPassword">
					<view class="tui-item-box">
						<image src="../../static/mima.png" mode="" style="width: 48rpx;height: 48rpx;"></image>
						<text class="tui-list-cell_name">修改密码</text>
					</view>
				</tui-list-cell>
				<tui-list-cell :arrow="true" @click="onClickedit">
					<view class="tui-item-box">
						<image src="../../static/set.png" mode="" style="width: 48rpx;height: 48rpx;"></image>
						<text class="tui-list-cell_name">设置</text>
					</view>
				</tui-list-cell>
			</tui-list-view>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import {
		mapMutations,
		mapActions,
		mapState
	} from 'vuex';

	export default {
		data() {
			return {

			};
		},
		computed: {
			...mapState({
				showLoginTip: state => state.login.showLoginTip,
				userInfo: state => state.login.userInfo,
			})
		},
		onShow() {
			if (!this.showLoginTip && JSON.stringify(this.userInfo) != '{}') {
				console.log(1)
			} else {
				console.log(2)
				this.$store.commit('LOGIN_TIP', true)
			}
		},
		methods: {
			// 设置
			onClickedit() {
				uni.navigateTo({
					url: './edit'
				})
			},
			onClickPath() {
				uni.navigateTo({
					url: '../Client/Client'
				})
			},
			onClickPathOrder() {
				uni.navigateTo({
					url: '../Order/List'
				})
			},
			// 修改密码
			onClickPassword() {
				uni.navigateTo({
					url: '../Login/register'
				})
			}
		}
	}
</script>

<style lang="less">
	.tui-item-box {
		width: 100%;
		display: flex;
		align-items: center;
		padding: 20rpx;

	}

	.tui-list-cell_name {
		padding-left: 20rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.tab-list {
		width: 691rpx;
		height: 493rpx;
		background: #FFFFFF;
		box-shadow: 0px 4rpx 8rpx 0px rgba(66, 137, 253, 0.1);
		border-radius: 20rpx;
		margin: 0 auto;
		margin-top: 20rpx;
	}

	.header-bg {
		height: 391rpx;
		background: url(../../static/my-bg.png) no-repeat;
		background-size: 100% 100%;
		display: flex;
		align-items: center;
		justify-content: center;

		.userInfo {
			width: 100%;
			padding: 20rpx;
			// height: 200rpx;
			display: flex;
			align-items: center;

			.userInfo-name {
				font-size: 32rpx;
				font-family: PingFang SC;
				font-weight: 600;
				color: #FFFFFF;

				text {
					font-size: 24rpx;
					font-family: PingFang SC;
					font-weight: 400;
					color: #FFFFFF;

				}
			}

			.userInfo-scroll {
				font-size: 24rpx;
				font-family: PingFang SC;
				font-weight: 500;
				color: #FFFFFF;
				padding: 24rpx 0 0 0;
			}
		}
	}
</style>
