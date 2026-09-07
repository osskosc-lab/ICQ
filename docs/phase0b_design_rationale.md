# Phase 0B Design Rationale

This note records why Phase 0B changes the intervention variable rather than modifying the Phase 0A threshold.

## Interventionist basis

The attached review of Woodward's *Making Things Happen* frames causal explanation in terms of how a phenomenon changes under intervention and emphasizes direct control of the tested variable while blocking irrelevant causal paths.

The attached paper *Causal Entropy and Information Gain for Measuring Causal Control* formalizes atomic intervention in an SCM as replacement of the intervened variable's structural assignment. Under an atomic intervention, the intervened variable no longer inherits its ordinary parents. The same paper distinguishes predictive relevance from causal control: confounded predictive association is not sufficient for causal interpretation.

These points map directly onto the P0A-4B failure:

```text
Z -> Q
Z x U -> Y
Q -/-> Y
```

Conditioning on Q cannot determine whether Q is causal or merely a proxy for Z. Replacing Q's structural assignment with do(Q) can, in the declared synthetic SCM, break the proxy relation.

## Falsification and confirmation discipline

The attached preregistration/falsification study (arXiv:2606.31511v1) separates discovery from confirmation, uses fresh seed namespaces, placebo-style controls, and executable audit invariants. Phase 0B adopts the same methodological separation:

```text
debug seeds != qualification seeds
audit verdict != scientific verdict
historical failure != erased by later redesign
```

Phase 0A remains frozen and is not rewritten if Phase 0B succeeds.

## Phenomenal firewall

The attached Chalmers paper distinguishes functional questions such as access, reportability, and control from the problem of subjective experience. Phase 0B concerns causal efficacy and intervention response only.

Therefore:

```text
L4 causal identification
does not imply
L5 phenomenal identification
```

No consciousness or qualia claim is part of Phase 0B.
