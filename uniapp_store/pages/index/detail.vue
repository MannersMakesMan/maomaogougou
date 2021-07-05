<!--本页面由uniapp切片工具生成，uni-app切片-可视化设计工具(一套代码编译到7个平台iOS、Android、H5、小程序)，软件下载地址：http://www.ymznkf.com/new_view_669.htm -->
<template>
	<view class="content">
		<view class="order_details_1">

			<view class="order_details_2">
				<view class="goods">
					<view v-for="(item, index) in itemInfo.goods_data" :key="index" class="row">
						<image :src="showImg(item.sku.default_image_url)" mode="scaleToFill" border="0" class="pic">
						</image>
						<view class="order_details_10">
							<text decode="true" class="good">{{item.sku.name}}</text>
							<text decode="true" class="num">数量：{{item.count}}</text>
						</view>
						<text decode="true" class="money">价格：{{item.sku.price}}</text>
					</view>
				</view>
				<view class="order_details_15">
					<text decode="true"
						class="order_details_16">共{{itemInfo.goods_data.length}}份小计￥{{itemInfo.total_amount}}</text>
				</view>
			</view>
			<view class="order_details_2">
				<tui-list-view color="#777">
					<tui-list-cell @click="detail" :hover="false">
						<view class="" style="display: flex;align-items: center;justify-content: space-between;">
							<view class="">
								定量创建人：
							</view>
							<view class="">
								{{itemInfo.user}}
							</view>
						</view>
					</tui-list-cell>
					<tui-list-cell @click="detail" :hover="false">
						<view class="" style="display: flex;align-items: center;justify-content: space-between;">
							<view class="">
								订单所属客户：
							</view>
							<view class="">
								{{itemInfo.client_user}}
							</view>
						</view>
					</tui-list-cell>
					<tui-list-cell @click="detail" :hover="false">
						<view class="" style="display: flex;align-items: center;justify-content: space-between;">
							<view class="">
								定量单总金额：
							</view>
							<view class="">
								{{itemInfo.total_amount}}
							</view>
						</view>
					</tui-list-cell>
					<tui-list-cell @click="detail" :hover="false">
						<view class="" style="display: flex;align-items: center;justify-content: space-between;">
							<view class="">
								订单类型：
							</view>
							<view class="">
								{{itemInfo.order_type == 1 ? '定量' : '增量'}}
							</view>
						</view>
					</tui-list-cell>
					<tui-list-cell @click="detail" :hover="false">
						<view class="" style="display: flex;align-items: center;justify-content: space-between;">
							<view class="">
								创建时间：
							</view>
							<view class="">
								{{itemInfo.create_time}}
							</view>
						</view>
					</tui-list-cell>

				</tui-list-view>
			</view>
		</view>
		<!-- 登录弹框 -->
		<shopro-login-modal></shopro-login-modal>
	</view>
</template>

<script>
	import baseUrl from '../../api/config.js'
	export default {
		data() {
			return {
				itemInfo: {}
			}
		},
		onLoad(options) {
			this.itemInfo = JSON.parse(options.data)
			console.log(this.itemInfo)
		},
		methods: {
			showImg(img) {
				return baseUrl + img
			}
		}
	}
</script>

<style lang="scss" scoped>
	//本页面由uniapp切片工具生成，uni-app切片-可视化设计工具(一套代码编译到7个平台iOS、Android、H5、小程序)，软件下载地址：http://www.ymznkf.com/new_view_669.htm
	html,
	body,
	#app {
		height: 100%;
		width: 100%;
	}

	.content {
		height: 100%;
		width: 100%;
	}

	uni-page-body,
	#app {
		height: 100%;
	}

	button::after {
		border: none;
		width: auto;
	}

	input {
		outline: none;
		border: none;
		list-style: none;
		width: auto;
	}

	.list_item {
		float: left;
	}

	.ym_hide {
		display: none;
	}

	.ym_show {
		display: block;
	}

	.slide-image {
		width: 100%;
		height: 100%;
	}

	.list_horizontal {
		width: auto;
		display: inline-block;
	}

	.order_details_1 {
		white-space: normal;
		width: 749upx;
		height: 100%;
		padding: 0upx;
		clear: both;
		float: left;
		background-color: #f6f6f6;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_7 {
		white-space: normal;
		width: 749upx;
		height: 164upx;
		padding-left: 0upx;
		padding-right: 0upx;
		padding-top: 0upx;
		padding-bottom: 20upx;
		clear: both;
		margin-top: 0upx;
		margin-left: 0upx;
		float: left;
		background-color: #fd773c;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_7 .status {
		white-space: normal;
		width: 362upx;
		height: 62upx;
		padding: 0upx;
		clear: both;
		margin-top: 52upx;
		margin-left: 29upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #ffffff;
		font-size: 49upx;
		line-height: 62upx;
	}

	.order_details_1 .order_details_7 .smallTitle {
		white-space: normal;
		width: 452upx;
		height: 38upx;
		padding: 0upx;
		clear: both;
		margin-top: 6upx;
		margin-left: 29upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #ffffff;
		font-size: 26upx;
		line-height: 38upx;
	}

	.order_details_1 .order_details_2 {
		white-space: normal;
		width: 690upx;
		padding: 0upx;
		clear: both;
		margin-top: 20upx;
		margin-left: 29upx;
		float: left;
		background-color: #ffffff;
		text-align: left;
		border-color: #e1e1e1;
		border-width: 1upx;
		border-style: solid;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .goods {
		white-space: normal;
		width: 690upx;
		min-height: 121upx;
		padding-left: 0upx;
		padding-right: 0upx;
		padding-top: 0upx;
		padding-bottom: 20upx;
		clear: both;
		margin-top: 0upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-bottom-color: #e1e1e1;
		border-bottom-width: 1upx;
		border-bottom-style: solid;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .goods .row {
		white-space: normal;
		width: 643upx;
		height: 113upx;
		padding: 0upx;
		margin-top: 18upx;
		margin-left: 24upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .goods .row .pic {
		white-space: normal;
		width: 91upx;
		height: 90upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 4upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
		line-height: 90upx;
	}

	.order_details_1 .order_details_2 .goods .row .order_details_10 {
		white-space: normal;
		width: 372upx;
		height: 91upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 15upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .goods .row .order_details_10 .good {
		white-space: normal;
		width: 366upx;
		height: 43upx;
		padding: 0upx;
		clear: both;
		margin-top: 0upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #646464;
		font-size: 33upx;
		line-height: 43upx;
	}

	.order_details_1 .order_details_2 .goods .row .order_details_10 .num {
		white-space: normal;
		width: 234upx;
		height: 29upx;
		padding: 0upx;
		clear: both;
		margin-top: 12upx;
		margin-left: 0upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		color: #646464;
		font-size: 22upx;
		line-height: 29upx;
	}

	.order_details_1 .order_details_2 .goods .row .money {
		white-space: normal;
		width: 138upx;
		height: 36upx;
		padding: 0upx;
		margin-top: 13upx;
		margin-left: 19upx;
		float: left;
		text-align: right;
		border-radius: 0upx;
		color: #000000;
		font-size: 24upx;
		line-height: 36upx;
	}

	.order_details_1 .order_details_2 .order_details_15 {
		white-space: normal;
		width: 416upx;
		height: 79upx;
		padding: 0upx;
		clear: both;
		margin-top: 33upx;
		margin-left: 265upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
	}

	.order_details_1 .order_details_2 .order_details_15 .order_details_16 {
		white-space: normal;
		width: 399upx;
		height: 49upx;
		padding: 0upx;
		margin-top: 0upx;
		margin-left: 4upx;
		float: left;
		text-align: right;
		border-radius: 0upx;
		color: #646464;
		font-size: 34upx;
		line-height: 49upx;
	}

	.order_details_1 .banner {
		white-space: normal;
		width: 690upx;
		height: 270upx;
		padding: 0upx;
		clear: both;
		margin-top: 29upx;
		margin-left: 29upx;
		float: left;
		text-align: left;
		border-radius: 0upx;
		font-size: 8upx;
		line-height: 270upx;
	}

	.order_details_1 .btAdd {
		white-space: normal;
		width: 690upx;
		height: 87upx;
		padding: 0upx;
		clear: both;
		margin-top: 64upx;
		margin-left: 29upx;
		float: left;
		background-color: #fdb71b;
		text-align: center;
		justify-content: center;
		border-radius: 40upx;
		color: #ffffff;
		font-size: 36upx;
		line-height: 87upx;
	}
</style>
