export function groupBy(items, accessor){
	return items.reduce((m, e) =>
		m.set(accessor(e), [...m.get(accessor(e)) || [], e]),
		new Map()
	)
}
