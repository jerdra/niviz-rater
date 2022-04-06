<!--
	Clickable QC tile object that returns its ID when clicked
		- name
		- failed
		- id
-->

<script>

	import { createEventDispatcher } from 'svelte';

  export let id;
	export let label;
  export let failed;

	const dispatch = createEventDispatcher();

	function handleClick(){
		dispatch(
			'message', {
				id: id
			}
		)
	}

	function getClass(status){
		
		let modifier;
		if (status == true){
			modifier = "is-danger"
		} else if (status == false){
			modifier = "is-success"
		} else {
			modifier = ""
		}
		return `column is-2 box is-clickable notification ${modifier}`
	}

	let tileClass;
	$:tileClass = getClass(failed);


</script>

<div on:click={(id) ? handleClick : ''} class='{tileClass}'>
		<strong>{label}</strong>
</div>

<style>
	.column.box{
		-webkit-filter: brightness(100%);
	}

	.column.box:hover{
		-webkit-filter: brightness(90%);
		transition: all 0.30s ease;
	}

	.notification:not(:last-child){
		margin-bottom:0;
	}
</style>
