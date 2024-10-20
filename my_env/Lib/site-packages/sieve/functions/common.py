import sieve 
from typing import List, Iterator

@sieve.function(name="sieve-common/flatten", gpu = False)
def flatten(list_input: List[sieve.Struct]) -> Iterator[sieve.Struct]:
    for i in list_input:
        for j in i:
            yield j

# In memory join
@sieve.function(name="sieve-common/temporal-join", gpu = False)
def temporal_join(*iterators: Iterator[sieve.Temporal]) -> Iterator[sieve.Temporal]:
    iterators = list(iterators)
    iterators = [iter(i) for i in iterators]
    while True:
        try:
            items = [next(i) for i in iterators]
            if len(set([i.timestamp for i in items])) != 1:
                raise Exception("Timestamps do not match")
            yield sieve.Temporal(timestamp=items[0].timestamp, data=sieve.Struct(**{f"data{i}": j.data for i, j in enumerate(items)}))
        except StopIteration:
            break