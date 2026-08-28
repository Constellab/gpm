# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Cross-repo work**: read [`monorepo-back/docs/architecture/platform-map.md`](../monorepo-back/docs/architecture/platform-map.md) (sibling repository) when a change spans repositories, when cutting a release, or when a cross-repo inconsistency looks like a bug — it holds the version chain, the release ordering, and the deliberate oddities.

This repository is one piece of the lab compute plane; most of what it does only makes sense
alongside `lab-manager`, `gws_core` and the Space API. The map above is the shortest route to that
context.
