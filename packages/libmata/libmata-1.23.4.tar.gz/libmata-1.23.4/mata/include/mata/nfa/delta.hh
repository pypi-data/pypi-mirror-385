// TODO: Insert file header.

#ifndef MATA_DELTA_HH
#define MATA_DELTA_HH

#include "mata/utils/sparse-set.hh"
#include "mata/utils/synchronized-iterator.hh"
#include "mata/alphabet.hh"
#include "mata/nfa/types.hh"

#include <iterator>

namespace mata::nfa {

/// A single transition in Delta represented as a triple(source, symbol, target).
struct Transition {
    State source; ///< Source state.
    Symbol symbol; ///< Transition symbol.
    State target; ///< Target state.

    Transition() : source(), symbol(), target() { }
    Transition(const Transition&) = default;
    Transition(Transition&&) = default;
    Transition &operator=(const Transition&) = default;
    Transition &operator=(Transition&&) = default;
    Transition(const State source, const Symbol symbol, const State target)
            : source(source), symbol(symbol), target(target) {}

    auto operator<=>(const Transition&) const = default;
};

/**
 * Move from a @c StatePost for a single source state, represented as a pair of @c symbol and target state @c target.
 */
class Move {
public:
    Symbol symbol;
    State target;

    bool operator==(const Move&) const = default;
}; // class Move.

/**
 * Structure represents a post of a single @c symbol: a set of target states in transitions.
 *
 * A set of @c SymbolPost, called @c StatePost, is describing the automata transitions from a single source state.
 */
class SymbolPost {
public:
    Symbol symbol{};
    StateSet targets{};

    SymbolPost() = default;
    explicit SymbolPost(Symbol symbol) : symbol{ symbol }, targets{} {}
    SymbolPost(Symbol symbol, State state_to) : symbol{ symbol }, targets{ state_to } {}
    SymbolPost(Symbol symbol, StateSet states_to) : symbol{ symbol }, targets{ std::move(states_to) } {}

    SymbolPost(SymbolPost&& rhs) noexcept : symbol{ rhs.symbol }, targets{ std::move(rhs.targets) } {}
    SymbolPost(const SymbolPost& rhs) = default;
    SymbolPost& operator=(SymbolPost&& rhs) noexcept;
    SymbolPost& operator=(const SymbolPost& rhs) = default;

    std::weak_ordering operator<=>(const SymbolPost& other) const { return symbol <=> other.symbol; }
    bool operator==(const SymbolPost& other) const { return symbol == other.symbol; }

    StateSet::iterator begin() { return targets.begin(); }
    StateSet::iterator end() { return targets.end(); }

    StateSet::const_iterator cbegin() const { return targets.cbegin(); }
    StateSet::const_iterator cend() const { return targets.cend(); }

    size_t count(State s) const { return targets.count(s); }
    bool empty() const { return targets.empty(); }
    size_t num_of_targets() const { return targets.size(); }

    void insert(State s);
    void insert(const StateSet& states);

    // THIS BREAKS THE SORTEDNESS INVARIANT,
    // dangerous,
    // but useful for adding states in a random order to sort later (supposedly more efficient than inserting in a random order)
    void inline push_back(const State s) { targets.push_back(s); }

    template <typename... Args>
    StateSet& emplace_back(Args&&... args) {
	// Forwardinng the variadic template pack of arguments to the emplace_back() of the underlying container.
        return targets.emplace_back(std::forward<Args>(args)...);
    }

    void erase(State s) { targets.erase(s); }

    std::vector<State>::const_iterator find(State s) const { return targets.find(s); }
    std::vector<State>::iterator find(State s) { return targets.find(s); }
}; // class mata::nfa::SymbolPost.

/**
 * @brief A data structure representing possible transitions over different symbols from a source state.
 *
 * It is an ordered vector containing possible @c SymbolPost (i.e., pair of symbol and target states).
 * @c SymbolPosts in the vector are ordered by symbols in @c SymbolPosts.
 */
class StatePost : private utils::OrdVector<SymbolPost> {
private:
    using super = utils::OrdVector<SymbolPost>;
public:
    using super::iterator, super::const_iterator;
    using super::begin, super::end, super::cbegin, super::cend;
    using super::OrdVector;
    using super::operator=;
    using super::operator==;
    StatePost(const StatePost&) = default;
    StatePost(StatePost&&) = default;
    StatePost& operator=(const StatePost&) = default;
    StatePost& operator=(StatePost&&) = default;
    bool operator==(const StatePost&) const = default;
    using super::insert;
    using super::reserve;
    using super::empty, super::size;
    using super::to_vector;
    // dangerous, breaks the sortedness invariant
    using super::push_back, super::emplace_back;
    // is adding non-const version as well ok?
    using super::front;
    using super::back;
    using super::pop_back;
    using super::filter;
    using super::clear;

    using super::erase;

    using super::find;
    iterator find(const Symbol symbol) {
        static SymbolPost symbol_post{};
        symbol_post.symbol = symbol;
        return super::find(symbol_post);
    }
    const_iterator find(const Symbol symbol) const {
        static SymbolPost symbol_post{};
        symbol_post.symbol = symbol;
        return super::find(symbol_post);
    }

    ///returns an iterator to the smallest epsilon, or end() if there is no epsilon
    const_iterator first_epsilon_it(Symbol first_epsilon) const;

    /**
     * @brief Get the set of all target states in the @c StatePost.
     * @return Set of all target states in the @c StatePost.
     */
    StateSet get_successors() const;

    /**
     * @brief Returns a reference to target states for a given symbol in the @c StatePost.
     *
     * If there is no such symbol, a static empty set is returned.
     *
     * @param symbol Symbol to get the successors for.
     * @return Set of target states for the given symbol.
     */
    const StateSet& get_successors(Symbol symbol) const;

    /**
     * @brief Iterator over moves represented as @c Move instances.
     *
     * It iterates over pairs (symbol, target) for the given @c StatePost.
     */
    class Moves {
    public:
        Moves() = default;
        /**
         * @brief construct moves iterating over a range @p symbol_post_it (including) to @p symbol_post_end (excluding).
         *
         * @param[in] state_post State post to iterate over.
         * @param[in] symbol_post_it First iterator over symbol posts to iterate over.
         * @param[in] symbol_post_end End iterator over symbol posts (which functions as an sentinel; is not iterated over).
         */
        Moves(const StatePost& state_post, StatePost::const_iterator symbol_post_it, StatePost::const_iterator symbol_post_end);
        Moves(Moves&&) = default;
        Moves(Moves&) = default;
        Moves& operator=(Moves&& other) noexcept;
        Moves& operator=(const Moves& other) noexcept;

        class const_iterator;
        const_iterator begin() const;
        const_iterator end() const;

    private:
        const StatePost* state_post_{ nullptr };
        StatePost::const_iterator symbol_post_it_{}; ///< Current symbol post iterator to iterate over.
        /// End symbol post iterator which is no longer iterated over (one after the last symbol post iterated over or
        ///  end()).
        StatePost::const_iterator symbol_post_end_{};
    }; // class Moves.

    /**
     * Iterator over all moves (over all labels) in @c StatePost represented as @c Move instances.
     */
    Moves moves() const { return { *this, this->cbegin(), this->cend() }; }
    /**
     * Iterator over specified moves in @c StatePost represented as @c Move instances.
     *
     * @param[in] symbol_post_it First iterator over symbol posts to iterate over.
     * @param[in] symbol_post_end End iterator over symbol posts (which functions as an sentinel, is not iterated over).
     */
    Moves moves(StatePost::const_iterator symbol_post_it, StatePost::const_iterator symbol_post_end) const;
    /**
     * Iterator over epsilon moves in @c StatePost represented as @c Move instances.
     */
    Moves moves_epsilons(Symbol first_epsilon = EPSILON) const;
    /**
     * Iterator over alphabet (normal) symbols (not over epsilons) in @c StatePost represented as @c Move instances.
     */
    Moves moves_symbols(Symbol last_symbol = EPSILON - 1) const;

    /**
     * Count the number of all moves in @c StatePost.
     */
    size_t num_of_moves() const;
}; // class StatePost.

/**
 * Iterator over moves.
 */
class StatePost::Moves::const_iterator {
private:
    const StatePost* state_post_{ nullptr };
    StatePost::const_iterator symbol_post_it_{};
    StateSet::const_iterator target_it_{};
    StatePost::const_iterator symbol_post_end_{};
    bool is_end_{ false };
    /// Internal allocated instance of @c Move which is set for the move currently iterated over and returned as
    ///  a reference with @c operator*().
    Move move_{};

public:
    using iterator_category = std::forward_iterator_tag;
    using value_type = Move;
    using difference_type = size_t;
    using pointer = Move*;
    using reference = Move&;

     /// Construct end iterator.
    const_iterator(): is_end_{ true } {}
    /// Const all moves iterator.
    const_iterator(const StatePost& state_post);
    /// Construct iterator from @p symbol_post_it (including) to @p symbol_post_it_end (excluding).
    const_iterator(const StatePost& state_post, StatePost::const_iterator symbol_post_it,
                   StatePost::const_iterator symbol_post_it_end);
    const_iterator(const const_iterator& other) noexcept = default;
    const_iterator(const_iterator&&) = default;

    const Move& operator*() const { return move_; }
    const Move* operator->() const { return &move_; }

    // Prefix increment
    const_iterator& operator++();
    // Postfix increment
    const const_iterator operator++(int);

    const_iterator& operator=(const const_iterator& other) noexcept = default;
    const_iterator& operator=(const_iterator&&) = default;

    bool operator==(const const_iterator& other) const;
}; // class const_iterator.

/**
 * @brief Specialization of utils::SynchronizedExistentialIterator for iterating over SymbolPosts.
 */
class SynchronizedExistentialSymbolPostIterator : public utils::SynchronizedExistentialIterator<utils::OrdVector<SymbolPost>::const_iterator> {
public:
    /**
     * @brief Get union of all targets.
     */
    StateSet unify_targets() const;

    /**
     * @brief Synchronize with the given SymbolPost @p sync.
     *
     * Alignes the synchronized iterator to the same symbol as @p sync.
     * @return True iff the synchronized iterator points to the same symbol as @p sync.
     */
    bool synchronize_with(const SymbolPost& sync);

    /**
     * @brief Synchronize with the given symbol @p sync_symbol.
     *
     * Alignes the synchronized iterator to the same symbol as @p sync_symbol.
     * @return True iff the synchronized iterator points to the same symbol as @p sync.
     */
    bool synchronize_with(Symbol sync_symbol);
}; // class SynchronizedExistentialSymbolPostIterator.

/**
 * @brief Delta is a data structure for representing transition relation.
 *
 * Transition is represented as a triple Trans(source state, symbol, target state). Move is the part (symbol, target
 *  state), specified for a single source state.
 * Its underlying data structure is vector of StatePost classes. Each index to the vector corresponds to one source
 *  state, that is, a number for a certain state is an index to the vector of state posts.
 * Transition relation (delta) in Mata stores a set of transitions in a four-level hierarchical structure:
 *  Delta, StatePost, SymbolPost, and a set of target states.
 * A vector of 'StatePost's indexed by a source states on top, where the StatePost for a state 'q' (whose number is
 *  'q' and it is the index to the vector of 'StatePost's) stores a set of 'Move's from the source state 'q'.
 * Namely, 'StatePost' has a vector of 'SymbolPost's, where each 'SymbolPost' stores a symbol 'a' and a vector of
 *  target states of 'a'-moves from state 'q'. 'SymbolPost's are ordered by the symbol, target states are ordered by
 *  the state number.
 */
class Delta {
public:
    inline static const StatePost empty_state_post; // When posts[q] is not allocated, then delta[q] returns this.

    Delta(): state_posts_{} {}
    Delta(const Delta& other) = default;
    Delta(Delta&& other) = default;
    explicit Delta(size_t n): state_posts_{ n } {}

    Delta& operator=(const Delta& other) = default;
    Delta& operator=(Delta&& other) = default;

    bool operator==(const Delta& other) const;

    void reserve(size_t n) {
        state_posts_.reserve(n);
    };

    /**
     * @brief Get constant reference to the state post of @p source.
     *
     * If we try to access a state post of a @p source which is present in the automaton as an initial/final state,
     *  yet does not have allocated space in @c Delta, an @c empty_post is returned. Hence, the function has no side
     *  effects (no allocation is performed; iterators remain valid).
     * @param source[in] Source state of a state post to access.
     * @return State post of @p source.
     */
    const StatePost& state_post(const State source) const {
        if (source >= num_of_states()) {
            return empty_state_post;
        }
        return state_posts_[source];
    }

    /**
     * @brief Get constant reference to the state post of @p source.
     *
     * If we try to access a state post of a @p source which is present in the automaton as an initial/final state,
     *  yet does not have allocated space in @c Delta, an @c empty_post is returned. Hence, the function has no side
     *  effects (no allocation is performed; iterators remain valid).
     * @param source[in] Source state of a state post to access.
     * @return State post of @p source.
     */
    const StatePost& operator[](const State source) const { return state_post(source); }

    /**
     * @brief Get mutable (non-constant) reference to the state post of @p source.
     *
     * The function allows modifying the state post.
     *
     * BEWARE, IT HAS A SIDE EFFECT.
     *
     * If we try to access a state post of a @p source which is present in the automaton as an initial/final state,
     *  yet does not have allocated space in @c Delta, a new state post for @p source will be allocated along with
     *  all state posts for all previous states. This in turn may cause that the entire post data structure is
     *  re-allocated. Iterators to @c Delta will get invalidated.
     * Use the constant 'state_post()' is possible. Or, to prevent the side effect from causing issues, one might want
     *  to make sure that posts of all states in the automaton are allocated, e.g., write an NFA method that allocate
     *  @c Delta for all states of the NFA.
     * @param source[in] Source state of a state post to access.
     * @return State post of @p source.
     */
    StatePost& mutable_state_post(State source);

    void defragment(const BoolVector& is_staying, const std::vector<State>& renaming);

    template <typename... Args>
    StatePost& emplace_back(Args&&... args) {
	// Forwarding the variadic template pack of arguments to the emplace_back() of the underlying container.
        return state_posts_.emplace_back(std::forward<Args>(args)...);
    }

    void clear() { state_posts_.clear(); }

    /**
     * @brief Allocate state posts up to @p num_of_states states, creating empty @c StatePost for yet unallocated state
     *  posts.
     *
     * @param[in] num_of_states Number of states in @c Delta to allocate state posts for. Have to be at least
     *  num_of_states() + 1.
     */
    void allocate(const size_t num_of_states) {
        assert(num_of_states >= this->num_of_states());
        state_posts_.resize(num_of_states);
    }

    /**
     * @return Number of states in the whole Delta, including both source and target states.
     */
    size_t num_of_states() const { return state_posts_.size(); }

    /**
     * Check whether the @p state is used in @c Delta.
     */
    bool uses_state(const State state) const { return state < num_of_states(); }

    /**
     * @return Number of transitions in Delta.
     */
    size_t num_of_transitions() const;

    void add(State source, Symbol symbol, State target);
    void add(const Transition& trans) { add(trans.source, trans.symbol, trans.target); }
    void remove(State source, Symbol symbol, State target);
    void remove(const Transition& transition) { remove(transition.source, transition.symbol, transition.target); }

    /**
     * Check whether @c Delta contains a passed transition.
     */
    bool contains(State source, Symbol symbol, State target) const;
    /**
     * Check whether @c Delta contains a transition passed as a triple.
     */
    bool contains(const Transition& transition) const;

    /**
     * Check whether automaton contains no transitions.
     * @return True if there are no transitions in the automaton, false otherwise.
     */
    bool empty() const;

    /**
     * @brief Append post vector to the delta.
     *
     * @param post_vector Vector of posts to be appended.
     */
    void append(const std::vector<StatePost>& post_vector) {
        for(const StatePost& pst : post_vector) {
            this->state_posts_.push_back(pst);
        }
    }

    /**
     * @brief Copy posts of delta and apply a lambda update function on each state from
     * targets.
     *
     * IMPORTANT: In order to work properly, the lambda function needs to be
     * monotonic, that is, the order of states in targets cannot change.
     *
     * @param target_renumberer Monotonic lambda function mapping states to different states.
     * @return std::vector<Post> Copied posts.
     */
    std::vector<StatePost> renumber_targets(const std::function<State(State)>& target_renumberer) const;

    /**
     * @brief Add transitions to multiple destinations
     *
     * @param source From
     * @param symbol Symbol
     * @param targets Set of states to
     */
    void add(const State source, const Symbol symbol, const StateSet& targets);

    using const_iterator = std::vector<StatePost>::const_iterator;
    const_iterator cbegin() const { return state_posts_.cbegin(); }
    const_iterator cend() const { return state_posts_.cend(); }
    const_iterator begin() const { return state_posts_.begin(); }
    const_iterator end() const { return state_posts_.end(); }

    class Transitions;

    /**
     * Iterator over transitions represented as @c Transition instances.
     */
    Transitions transitions() const;

    /**
     * Get transitions leading to @p state_to.
     * @param state_to[in] Target state for transitions to get.
     * @return Transitions leading to @p state_to.
     *
     * Operation is slow, traverses over all symbol posts.
     */
    std::vector<Transition> get_transitions_to(State state_to) const;

    /**
     * Get transitions from @p state_from to @p state_to.
     * @param state_from[in] Source state.
     * @param state_from[in] Target state.
     * @return Transitions from @p source to @p state_to.
     *
     * Operation is slow, traverses over all symbol posts.
     */
    std::vector<Transition> get_transitions_between(State state_from, State state_to) const;

    /**
     * Get the set of states that are successors of the given @p state.
     * @param[in] state State from which successors are checked.
     * @return Set of states that are successors of the given @p state.
     */
    StateSet get_successors(State state) const;

    const StateSet& get_successors(State state, Symbol symbol) const;

    StateSet get_successors(State state, Symbol symbol, EpsilonClosureOpt epsilon_closure_opt) const;

    /**
     * Iterate over @p epsilon symbol posts under the given @p state.
     * @param[in] state State from which epsilon transitions are checked.
     * @param[in] epsilon User can define his favourite epsilon or used default.
     * @return An iterator to @c SymbolPost with epsilon symbol. End iterator when there are no epsilon transitions.
     */
    StatePost::const_iterator epsilon_symbol_posts(State state, Symbol epsilon = EPSILON) const;

    /**
     * Iterate over @p epsilon symbol posts under the given @p state_post.
     * @param[in] state_post State post from which epsilon transitions are checked.
     * @param[in] epsilon User can define his favourite epsilon or used default.
     * @return An iterator to @c SymbolPost with epsilon symbol. End iterator when there are no epsilon transitions.
     */
    static StatePost::const_iterator epsilon_symbol_posts(const StatePost& state_post, Symbol epsilon = EPSILON);

    /**
     * @brief Expand @p target_alphabet by symbols from this delta.
     *
     * The value of the already existing symbols will NOT be overwritten.
     */
    void add_symbols_to(OnTheFlyAlphabet& target_alphabet) const;

    /**
     * @brief Get the set of symbols used on the transitions in the automaton.
     *
     * Does not necessarily have to equal the set of symbols in the alphabet used by the automaton.
     * @return Set of symbols used on the transitions.
     */
    utils::OrdVector<Symbol> get_used_symbols() const;

    utils::OrdVector<Symbol> get_used_symbols_vec() const;
    std::set<Symbol> get_used_symbols_set() const;
    utils::SparseSet<Symbol> get_used_symbols_sps() const;
    std::vector<bool> get_used_symbols_bv() const;
    BoolVector get_used_symbols_chv() const;

    /**
     * @brief Get the maximum non-epsilon used symbol.
     */
    Symbol get_max_symbol() const;
protected:
    std::vector<StatePost> state_posts_;
}; // class Delta.

/**
 * @brief Iterator over transitions represented as @c Transition instances.
 *
 * It iterates over triples (State source, Symbol symbol, State target).
 */
class Delta::Transitions {
public:
    Transitions() = default;
    explicit Transitions(const Delta* delta): delta_{ delta } {}
    Transitions(Transitions&&) = default;
    Transitions(Transitions&) = default;
    Transitions& operator=(Transitions&&) = default;
    Transitions& operator=(Transitions&) = default;

    class const_iterator;
    const_iterator begin() const;
    const_iterator end() const;
private:
    const Delta* delta_;
}; // class Transitions.

/**
 * Iterator over transitions.
 */
class Delta::Transitions::const_iterator {
private:
    const Delta* delta_ = nullptr;
    size_t current_state_{};
    StatePost::const_iterator state_post_it_{};
    StateSet::const_iterator symbol_post_it_{};
    bool is_end_{ false };
    Transition transition_{};

public:
    using iterator_category = std::forward_iterator_tag;
    using value_type = Transition;
    using difference_type = size_t;
    using pointer = Transition*;
    using reference = Transition&;

    const_iterator(): is_end_{ true } {}
    explicit const_iterator(const Delta& delta);
    const_iterator(const Delta& delta, State current_state);

    const_iterator(const const_iterator& other) noexcept = default;
    const_iterator(const_iterator&&) = default;

    const Transition& operator*() const { return transition_; }
    const Transition* operator->() const { return &transition_; }

    // Prefix increment
    const_iterator& operator++();
    // Postfix increment
    const const_iterator operator++(int);

    const_iterator& operator=(const const_iterator& other) noexcept = default;
    const_iterator& operator=(const_iterator&&) = default;

    bool operator==(const const_iterator& other) const;
}; // class Delta::Transitions::const_iterator.

} // namespace mata::nfa.

#endif //MATA_DELTA_HH
