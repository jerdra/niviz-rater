<!--
	@component

	Filterable Row component contains Entity components allowing
	users to examine rows containing failed QC, incomplete QC or passed QC

	Properties:
    rowName: Name of Row
-->

<script>
	export let rowName;
</script>

<!-- Row container -->
	<!-- This is a container that should contain another container -->
<div class="block notification is-primary m-5">
	<div class="columns is-multiline is-flex-gap">
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

  .is-flex-gap{
    gap: 0.35rem
  }
</style>
