<!--
	@component

	Filterable Row component contains Entity components allowing
	users to examine rows containing failed QC, incomplete QC or passed QC

	Properties:
		- entities: List of ordered entities stored 
		- orderSpec: Order specification for how to list entities
-->

<script>
	export let rowName;
</script>

<!-- Row container -->
	<!-- This is a container that should contain another container -->
<div class="block notification is-primary m-5">
	<div class="columns is-multiline">
		<div class="column notification is-warning is-12">
			<strong>{rowName}</strong>
		</div>
		<slot> </slot>
	</div>
</div>

<style>
	.notification:not(:last-child){
		margin-bottom: 0;
	}
</style>


<!--
To break down:

1. Row should just store styling component plus name of row (props)
2. Slots should be Entity tiles which is passed from parent
3. Pagination should be handled on two levels with just arrows and a number?
-->
