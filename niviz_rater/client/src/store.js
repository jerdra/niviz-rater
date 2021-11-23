import { writable, derived } from 'svelte/store';
import { groupBy } from './utils.js';
import { updateRating } from './db.js';


function createEntities(){
	/*
	 * Custom Svelte Store implementing the updateRating
	 * function to perform an update and refresh
	*/
	const { subscribe, set, update} = writable([]);

	// Entities implements createEntities and updateRating to push
	// rating to the DB
	return {
		subscribe,
		set, 
		updateRating: async (rating) => set(await updateRating(rating))
	}
}
export let entities = createEntities();

// groupSpec is a mapping from entity --> string that
// defines how to group entities
export let groupSpec = writable((e) => e.rowName);

// Provide a filtered view of Entities
export let groupedEntities = derived(
	[entities, groupSpec],
	([$entities, $groupSpec]) => {
		return groupBy(
			$entities.sort((a,b) => a.columnName - b.columnName), $groupSpec
		);
	}
);

// Convenience view into groupedEntities for using array indexing
export let entityWheel = derived(
	groupedEntities,
	$groupedEntities => {
		return [...$groupedEntities.values()].flat()
	}
)
