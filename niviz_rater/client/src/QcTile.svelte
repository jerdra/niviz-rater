<!--
	Clickable QC tile object that returns its ID when clicked
		- name
		- rating
		- id
-->

<script>

	import { createEventDispatcher } from 'svelte';

  export let id;
	export let label;
  export let rating;

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
		if (status == "Fail"){
			modifier = "is-danger"
		} else if (status == "Pass"){
			modifier = "is-success"
		} else if (status == "Uncertain") {
			modifier = "is-warning"
		} else if (status == "None") {
      modifier = ""
    }
		return `column is-2 box is-clickable notification ${modifier}`
	}

	let tileClass;
	$:tileClass = getClass(rating);


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
