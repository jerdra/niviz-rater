<!--
	@component

	Modal for displaying primary QC interface for interacting
	with and updating QC ratings
-->

<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { fly, slide, fade } from 'svelte/transition';
	import ModalEntityData from './ModalEntityData.svelte';

	export let entity;
	const dispatch = createEventDispatcher();
	let entityRating = {};
	let originalRating = {};
	let modalData;

	// Initialize entityRating
	entityRating.failed = entity.entityFailed;
	entityRating.comment = entity.entityComment;
	entityRating.id = entity.entityId
	if (entity.entityRating == null){
		entityRating.rating = null
	} else {
		entityRating.rating = entity.entityRating.id;
	}
	originalRating = Object.assign(originalRating, entityRating);

	const isSame = (a,b) => {
		return(
		Object.entries(a)
			.every(([k, v]) => b[k] == v)
		)
	}

	// Functions to deal with messaging logic
	$: msg = { rating: entityRating }
	const handleClose = () => {
		let result = true;
		const changed = !isSame(originalRating, entityRating);
		if (changed){
			result = window.confirm("Do you want to save changes?");
		}
		if (result) {
			dispatch('close',msg);
		} else {
			dispatch('close', { rating: originalRating });
		}
	}
	const handleNext = () => dispatch('next',msg);
	const handlePrevious = () => dispatch('previous',msg);

	// EventListener setups
	function handleKeydown(event){
		const key = event.key;
		const keyCode = event.keyCode;
		if (!modalData.commentFocused()){
			switch (key){
				case "n":
						handleNext();
					break;
				case "b":
						handlePrevious();
					break;
				case "z":
					modalData.setPass();
					break;
				case "x":
					modalData.setFail();
					break;
				case "c":
					modalData.setNone();
					break;
				case "Escape":
					handleClose();
					break;
				default:
					if (!isNaN(key)){
						modalData.setRating(parseInt(key));
					}
			}
		} else if (key == "Escape") {
			handleClose();
		}
	}

</script>
	<svelte:window on:keydown={handleKeydown}/>

	<div class="modal is-active"
	  transition:fade="{{ delay: 200, duration: 150 }}"
	  >
		<div class="modal-background" on:click={handleClose}></div>
		<div class="modal-card"
	   >
			<header class="modal-card-head">
				<p class="modal-card-title"> {entity.entityName} </p>
				<button on:click={handleClose} class="delete"></button>
			</header>

			<section class="modal-card-body">
				<ModalEntityData 
					entity={entity}
					bind:this={modalData}
					bind:qc_rating={entityRating.failed}
					bind:comment={entityRating.comment}
					bind:rating_id={entityRating.rating}/>
			</section>

			<footer class="modal-card-foot">
				<button on:click={handlePrevious} class="button is-success">Previous</button>
				<button on:click={handleNext} class="button is-success">Next</button>
				<button on:click={handleClose} class="button is-warning">Exit</button>
			</footer>
		</div>
	</div>

<style>
	.modal-card{
		width: 80%
	}
</style>
