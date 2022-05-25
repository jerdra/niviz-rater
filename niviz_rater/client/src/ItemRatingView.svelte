<!--
	@component

	Display of Modal core contents including:
	- Images
	- Current rating
	- Comment box that can be updated
	- Dropdown containing available annotations
-->


<script>

	import { onMount, getContext } from 'svelte';

	export let item;
	export let rating;
	export let comment;
	export let annotation_id;
  const { getValidRatings } = getContext("validRatings");
	let focused = false;

	function markRadioDefault(node, checked){
		node.checked=checked;
	}

	let availableAnnotations = item.availableAnnotations.map(r => r.id);

	export function setAnnotation(num){
		if (availableAnnotations.includes(num)){
			annotation_id=num;
		} else {
			console.log("Not an available rating")
		}
	}

	export function commentFocused(){
		return focused;
	}

	const onFocus = () => focused=true;
	const onBlur = () => focused=false;
</script>

{#if item}
	{#each item.images as image (image)}
		<div class="block">
			<object width="100%" data={image} type="image/svg+xml">
				<img src={image}/>
			</object>
		</div>
	{/each}
	<div class="tile is-parent">
		<div class="tile is-parent is-vertical">
			<div class="tile is-child">
				<div class="select">
					<select bind:value={annotation_id}>
						{#each item.availableAnnotations as annotation (annotation)}
							<option value={annotation.id}>{annotation.name}</option>
						{/each}
					</select>
				</div>
			</div>
			<div class="tile is-child">
				<div class="control">
					{#each getValidRatings() as {id, name} (id)}
						<label class="radio">
							<input type="radio"
								  use:markRadioDefault={id == rating}
								  name="passfail"
								 value={id} bind:group={rating}>
							{name}
						</label>
					{/each}
				</div>
			</div>
		</div>
		<div class="tile is-child">
			Comments:
			<textarea bind:value={comment} on:focus={onFocus} on:blur={onBlur}
				class="textarea" placeholder="Comments"></textarea>
		</div>
	</div>
{/if}

<style>
</style>

