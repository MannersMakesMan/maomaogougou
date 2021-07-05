<template>
	<view class="container">
		<view class="" style="padding-top: 20rpx;">
			<view class="item-box">
				<view class="item-name">
					{{detailInfo.shop_name || '暂无店铺名'}}
				</view>
				<view class="" style="width: 690rpx;border: 1rpx solid #DDDDDD;margin: 0 auto;">

				</view>
				<view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						联系方式
					</view>
					<view class="">
						{{detailInfo.phone}}
					</view>
				</view>
				<!-- <view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						微信号
					</view>
					<view class="">
						{{detailInfo.v_chart_number}}
					</view>
				</view> -->
				<view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						详细地址
					</view>
					<view class="">
						{{detailInfo.store_address}}
					</view>
				</view>
				<!-- <view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						店铺名
					</view>
					<view class="">
						{{detailInfo.shop_name}}
					</view>
				</view> -->
				<view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						客户类型
					</view>
					<view class="">
						{{detailInfo.client_type == 1 ? '潜在客户' : '有效客户'}}
					</view>
				</view>
				<view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						地址信息
					</view>
					<view class="">
						{{detailInfo.address || '无'}}
					</view>
				</view>
				<!-- <view class=""
					style="display: flex;align-items: center;justify-content: space-between;padding: 20rpx;font-size: 20rpx;">
					<view class="">
						地区
					</view>
					<view class="">
						{{detailInfo.address_districts + detailInfo.address_city + detailInfo.address_provincial}}
					</view>
				</view> -->

			</view>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				detailInfo: {}
			};
		},
		onLoad(options) {
			this.detailInfo = JSON.parse(options.data)
		}
	}
</script>

<style lang="less">
	.container {
		padding-bottom: env(safe-area-inset-bottom);
		background-color: #fff;
	}

	.item-box {
		

		.item-name {
			font-size: 22rpx;
			color: #333;
			font-weight: bold;
			padding: 20rpx;
			// border-bottom: 1rpx solid #DDDDDD;
		}
	}
</style>
