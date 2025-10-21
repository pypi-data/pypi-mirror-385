/* strings.hh -- Operations on NFAs/NFTs for string solving.
 */

#ifndef MATA_STRING_SOLVING_HH_
#define MATA_STRING_SOLVING_HH_

#include "mata/nfa/nfa.hh"
#include "mata/nft/nft.hh"

/**
 * NFA algorithms usable for solving string constraints.
 */
namespace mata::applications::strings {

using Nfa = nfa::Nfa;
using State = nfa::State;
using StateSet = nfa::StateSet;
using Transition = nfa::Transition;
using ParameterMap = nfa::ParameterMap;
using SymbolPost = nfa::SymbolPost;

using Nft = nft::Nft;

/**
 * Class mapping states to the shortest words accepted by languages of the states.
 */
class ShortestWordsMap {
public:
    /**
     * Maps states in the automaton @p aut to shortest words accepted by languages of the states.
     * @param aut Automaton to compute shortest words for.
     */
    explicit ShortestWordsMap(const Nfa& aut) : reversed_automaton(revert(aut)) {
        insert_initial_lengths();
        compute();
    }

    /**
     * Gets shortest words for the given @p states.
     * @param[in] states States to map shortest words for.
     * @return Set of shortest words.
     */
    std::set<Word> get_shortest_words_from(const StateSet& states) const;

    /**
     * Gets shortest words for the given @p state.
     * @param[in] state State to map shortest words for.
     * @return Set of shortest words.
     */
    std::set<Word> get_shortest_words_from(State state) const;

private:
    using WordLength = int; ///< A length of a word.
    /// Pair binding the length of all words in the word set and word set with words of the given length.
    using LengthWordsPair = std::pair<WordLength, std::set<Word>>;
    /// Map mapping states to the shortest words accepted by the automaton from the mapped state.
    std::unordered_map<State, LengthWordsPair> shortest_words_map{};
    std::set<State> processed{}; ///< Set of already processed states.
    std::deque<State> fifo_queue{}; ///< FIFO queue for states to process.
    const Nfa reversed_automaton; ///< Reversed input automaton.

    /**
     * @brief Inserts initial lengths into the shortest words map.
     *
     * Inserts initial length of length 0 for final state in the automaton (initial states in the reversed automaton).
     */
    void insert_initial_lengths();

    /**
     * Computes shortest words for all states in the automaton.
     */
    void compute();

    /**
     * Computes shortest words for the given @p state.
     * @param[in] state State to compute shortest words for.
     */
    void compute_for_state(State state);

    /**
     * Creates default shortest words mapping for yet unprocessed @p state.
     * @param[in] state State to map default shortest words.
     * @return Created default shortest words map element for the given @p state.
     */
    LengthWordsPair map_default_shortest_words(const State state) {
        return shortest_words_map.emplace(state, std::make_pair(-1, std::set<Word>{})).first->second;
    }

    /**
     * Update words for the current state.
     * @param[out] act Current state shortest words and length.
     * @param[in] dst Transition target state shortest words and length.
     * @param[in] symbol Symbol to update with.
     */
    static void update_current_words(LengthWordsPair& act, const LengthWordsPair& dst, Symbol symbol);
}; // Class ShortestWordsMap.

/**
 * Get shortest words (regarding their length) of the automaton using BFS.
 * @return Set of shortest words.
 */
std::set<Word> get_shortest_words(const Nfa& nfa);

/**
 * @brief Get the accepting words for each tape of @p nft with specific lengths
 * 
 * This function finds such an accepting word of @p nft that for each tape i,
 * the word on this tape (on the ith index of resulting vector) has the length lengths[i].
 * 
 * @param nft Transducer whose accepting words we are looking for
 * @param lengths The lengths of the words of each tape (size of lengths == the levels of @p nft)
 * @return std::optional<std::vector<Word>> Either the resulting words of tapes, or std::nullopt if such words of specific lengths do not exist
 */
std::optional<std::vector<Word>> get_words_of_lengths(const Nft& nft, std::vector<unsigned> lengths);

/**
 * @brief Get all the one symbol words accepted by @p nfa.
 */
std::set<Symbol> get_accepted_symbols(const Nfa& nfa);

/**
 * @brief Get the lengths of all words in the automaton @p aut. The function returns a set of pairs <u,v> where for each
 * such a pair there is a word with length u+k*v for all ks. The disjunction of such formulae of all pairs hence precisely
 * describe lengths of all words in the automaton.
 *
 * @param aut Input automaton
 * @return Set of pairs describing lengths
 */
std::set<std::pair<int, int>> get_word_lengths(const Nfa& aut);

/**
 * @brief Checks if the automaton @p nfa accepts only a single word \eps.
 *
 * @param nfa Input automaton
 * @return true iff L(nfa) = {\eps}
 */
bool is_lang_eps(const Nfa& nfa);

/**
 * Segment Automata including structs and algorithms.
 *
 * These are automata whose state space can be split into several segments connected by ε-transitions in a chain.
 * No other ε-transitions are allowed. As a consequence, no ε-transitions can appear in a cycle.
 * Segment automaton can have initial states only in the first segment and final states only in the last segment.
 */
namespace seg_nfa {

using SegNfa = Nfa;
using VisitedEpsMap = std::map<State, std::map<Symbol, unsigned>>;

/// Number of visited epsilons.
using VisitedEpsilonsCounterMap = std::map<Symbol, unsigned>;
/// Projection of VisitedEpsilonsNumberMap to sorted keys (in descending order).
using VisitedEpsilonsCounterVector = std::vector<unsigned>;

/**
* Class executing segmentation operations for a given segment automaton. Works only with segment automata.
*/
class Segmentation {
public:
    using EpsilonDepth = size_t; ///< Depth of ε-transitions.
    /// Dictionary of lists of ε-transitions grouped by their depth.
    /// For each depth 'i' we have 'depths[i]' which contains a list of ε-transitions of depth 'i'.
    using EpsilonDepthTransitions = std::unordered_map<EpsilonDepth, std::vector<Transition>>;
    using EpsilonDepthTransitionMap = std::unordered_map<EpsilonDepth, std::unordered_map<State, std::vector<Transition>>>;

    /**
     * Prepare automaton @p aut for segmentation.
     * @param[in] aut Segment automaton to make segments for.
     * @param[in] epsilon Symbol to execute segmentation for.
     */
    explicit Segmentation(const SegNfa& aut, const std::set<Symbol>& epsilons) : epsilons(epsilons), automaton(aut) {
        compute_epsilon_depths(); // Map depths to epsilon transitions.
    }

    /**
     * Get segmentation depths for ε-transitions.
     * @return Map of depths to lists of ε-transitions.
     */
    const EpsilonDepthTransitions& get_epsilon_depths() const { return epsilon_depth_transitions; }

    /**
     * Get the epsilon depth trans map object (mapping of depths and states to eps-successors)
     *
     * @return Map of depths to a map of states to transitions
     */
    const EpsilonDepthTransitionMap& get_epsilon_depth_trans_map() const { return this->eps_depth_trans_map; }

    /**
     * Get segment automata.
     * @return A vector of segments for the segment automaton in the order from the left (initial state in segment automaton)
     * to the right (final states of segment automaton).
     */
    const std::vector<Nfa>& get_segments();

    /**
     * Get raw segment automata.
     * @return A vector of segments for the segment automaton in the order from the left (initial state in segment automaton)
     * to the right (final states of segment automaton) without trimming (the states are same as in the original automaton).
     */
    const std::vector<Nfa>& get_untrimmed_segments();

    const VisitedEpsMap& get_visited_eps() const { return this->visited_eps; }

private:
    const std::set<Symbol> epsilons; ///< Symbol for which to execute segmentation.
    /// Automaton to execute segmentation for. Must be a segment automaton (can be split into @p segments).
    const SegNfa& automaton;
    EpsilonDepthTransitions epsilon_depth_transitions{}; ///< Epsilon depths.
    EpsilonDepthTransitionMap eps_depth_trans_map{}; /// Epsilon depths with mapping of states to epsilon transitions
    std::vector<SegNfa> segments{}; ///< Segments for @p automaton.
    std::vector<SegNfa> segments_raw{}; ///< Raw segments for @p automaton.
    VisitedEpsMap visited_eps{}; /// number of visited eps for each state

    /**
     * Pair of state and its depth.
     */
    struct StateDepthTuple {
        State state; ///< State with a depth.
        EpsilonDepth depth; ///< Depth of a state.
        VisitedEpsilonsCounterMap eps; /// visited epsilons and their numbers
    };

    /**
     * Compute epsilon depths with their transitions.
     */
    void compute_epsilon_depths();

    /**
     * Split segment @c automaton into @c segments.
     */
    void split_aut_into_segments();

    /**
     * Propagate changes to the current segment automaton to the next segment automaton.
     * @param[in] current_depth Current depth.
     * @param[in] transition Current epsilon transition.
     */
    void update_next_segment(size_t current_depth, const Transition& transition);

    /**
     * Update current segment automaton.
     * @param[in] current_depth Current depth.
     * @param[in] transition Current epsilon transition.
     */
    void update_current_segment(size_t current_depth, const Transition& transition);

    /**
     * Initialize map of visited states.
     * @return Map of visited states.
     */
    std::unordered_map<State, bool> initialize_visited_map() const;

    /**
     * Initialize worklist of states with depths to process.
     * @return Queue of state and its depth pairs.
     */
    std::deque<StateDepthTuple> initialize_worklist() const;

    /**
     * Process pair of state and its depth.
     * @param[in] state_depth_pair Current state depth pair.
     * @param[out] worklist Worklist of state and depth pairs to process.
     */
    void process_state_depth_pair(const StateDepthTuple& state_depth_pair, std::deque<StateDepthTuple>& worklist);

    /**
     * Add states with non-epsilon transitions to the @p worklist.
     * @param move[in] Move from current state.
     * @param depth[in] Current depth.
     * @param worklist[out] Worklist of state and depth pairs to process.
     */
    void add_transitions_to_worklist(const StateDepthTuple& state_depth_pair, const SymbolPost& move,
                                     std::deque<StateDepthTuple>& worklist);

    /**
     * Process epsilon transitions for the current state.
     * @param[in] state_depth_pair Current state depth pair.
     * @param[in] move Move from current state.
     * @param[out] worklist Worklist of state and depth pairs to process.
     */
    void handle_epsilon_transitions(const StateDepthTuple& state_depth_pair, const SymbolPost& move,
                                    std::deque<StateDepthTuple>& worklist);

    /**
     * @brief Remove inner initial and final states.
     *
     * Remove all initial states for all segments but the first one and all final states for all segments but the
     *  last one.
     */
    void remove_inner_initial_and_final_states();
}; // Class Segmentation.

/// A noodle is represented as a sequence of segments (a copy of the segment automata) created as if there was exactly
///  one ε-transition between each two consecutive segments.
using Noodle = std::vector<std::shared_ptr<SegNfa>>;
/// Segment with a counter of visited epsilons.
using SegmentWithEpsilonsCounter = std::pair<std::shared_ptr<Nfa>, VisitedEpsilonsCounterVector>;
/// Noodles as segments enriched with EpsCntMap
using NoodleWithEpsilonsCounter = std::vector<SegmentWithEpsilonsCounter>;

/**
 * @brief segs_one_initial_final
 *
 * segments_one_initial_final[init, final] is the pointer to automaton created from one of
 * the segments such that init and final are one of the initial and final states of the segment
 * and the created automaton takes this segment, sets initial={init}, final={final}
 * and trims it; also segments_one_initial_final[unused_state, final] is used for the first
 * segment (where we always want all initial states, only final state changes) and
 * segments_one_initial_final[init, unused_state] is similarly for the last segment
 * TODO: should we use unordered_map? then we need hash
 */
void segs_one_initial_final(
    const std::vector<Nfa>& segments, bool include_empty, const State& unused_state,
    std::map<std::pair<State, State>, std::shared_ptr<Nfa>>& out);

/**
 * @brief Create noodles from segment automaton @p aut.
 *
 * Segment automaton is a chain of finite automata (segments) connected via ε-transitions.
 * A noodle is a vector of pointers to copy of the segments automata created as if there was exactly one ε-transition
 *  between each two consecutive segments.
 *
 * @param[in] automaton Segment automaton to noodlify.
 * @param[in] epsilon Epsilon symbol to noodlify for.
 * @param[in] include_empty Whether to also include empty noodles.
 * @return A list of all (non-empty) noodles.
 */
std::vector<Noodle> noodlify(const SegNfa& aut, Symbol epsilon, bool include_empty = false);

/**
 * @brief Create noodles from segment automaton @p aut.
 *
 * Segment automaton is a chain of finite automata (segments) connected via ε-transitions.
 * A noodle is a vector of pointers to copy of the segments automata created as if there was exactly one ε-transition
 *  between each two consecutive segments.
 *
 * @param[in] automaton Segment automaton to noodlify.
 * @param[in] epsilons Epsilon symbols to noodlify for.
 * @param[in] include_empty Whether to also include empty noodles.
 * @return A list of all (non-empty) noodles.
 */
std::vector<NoodleWithEpsilonsCounter> noodlify_mult_eps(const SegNfa& aut, const std::set<Symbol>& epsilons, bool include_empty = false);

/**
 * @brief Create noodles for left and right side of equation.
 *
 * Segment automaton is a chain of finite automata (segments) connected via ε-transitions.
 * A noodle is a copy of the segment automaton with exactly one ε-transition between each two consecutive segments.
 *
 * Mata cannot work with equations, queries etc. Hence, we compute the noodles for the equation, but represent
 *  the equation in a way that libMata understands. The left side automata represent the left side of the equation
 *  and the right automaton represents the right side of the equation. To create noodles, we need a segment automaton
 *  representing the intersection. That can be achieved by computing a product of both sides. First, the left side
 *  has to be concatenated over an epsilon transitions into a single automaton to compute the intersection on, though.
 *
 * @param[in] lhs_automata Sequence of segment automata for left side of an equation to noodlify.
 * @param[in] rhs_automaton Segment automaton for right side of an equation to noodlify.
 * @param[in] include_empty Whether to also include empty noodles.
 * @param[in] params Additional parameters for the noodlification:
 *     - "reduce": "false", "forward", "backward", "bidirectional"; Execute forward, backward or bidirectional simulation
 *                 minimization before noodlification.
 * @return A list of all (non-empty) noodles.
 */
std::vector<Noodle> noodlify_for_equation(const std::vector<std::reference_wrapper<Nfa>>& lhs_automata,
                                     const Nfa& rhs_automaton,
                                     bool include_empty = false, const ParameterMap& params = {{ "reduce", "false"}});

/**
 * @brief Create noodles for left and right side of equation.
 *
 * Segment automaton is a chain of finite automata (segments) connected via ε-transitions.
 * A noodle is a copy of the segment automaton with exactly one ε-transition between each two consecutive segments.
 *
 * Mata cannot work with equations, queries etc. Hence, we compute the noodles for the equation, but represent
 *  the equation in a way that libMata understands. The left side automata represent the left side of the equation
 *  and the right automaton represents the right side of the equation. To create noodles, we need a segment automaton
 *  representing the intersection. That can be achieved by computing a product of both sides. First, the left side
 *  has to be concatenated over an epsilon transitions into a single automaton to compute the intersection on, though.
 *
 * @param[in] lhs_automata Sequence of pointers to segment automata for left side of an equation to noodlify.
 * @param[in] rhs_automaton Segment automaton for right side of an equation to noodlify.
 * @param[in] include_empty Whether to also include empty noodles.
 * @param[in] params Additional parameters for the noodlification:
 *     - "reduce": "false", "forward", "backward", "bidirectional"; Execute forward, backward or bidirectional simulation
 *                 minimization before noodlification.
 * @return A list of all (non-empty) noodles.
 */
std::vector<Noodle> noodlify_for_equation(
                const std::vector<Nfa*>& lhs_automata, const Nfa& rhs_automaton, bool include_empty = false,
                const ParameterMap& params = {{ "reduce", "false"}});

/**
 * @brief Create noodles for left and right side of equation (both sides are given as a sequence of automata).
 *
 * @param[in] lhs_automata Sequence of pointers to segment automata for left side of an equation to noodlify.
 * @param[in] rhs_automaton Sequence of pointers to segment automata for right side of an equation to noodlify.
 * @param[in] include_empty Whether to also include empty noodles.
 * @param[in] params Additional parameters for the noodlification:
 *     - "reduce": "false", "forward", "backward", "bidirectional"; Execute forward, backward or bidirectional simulation
 *                 minimization before noodlification.
 * @return A list of all (non-empty) noodles together with the positions reached from the beginning of left/right side.
 */
std::vector<NoodleWithEpsilonsCounter> noodlify_for_equation(
   const std::vector<std::shared_ptr<Nfa>>& lhs_automata,
   const std::vector<std::shared_ptr<Nfa>>& rhs_automata,
   bool include_empty = false, const ParameterMap& params = {{ "reduce", "false"}});

struct TransducerNoodleElement {
    std::shared_ptr<Nft> transducer;
    std::shared_ptr<Nfa> input_aut;
    unsigned input_index;
    std::shared_ptr<Nfa> output_aut;
    unsigned output_index;

    TransducerNoodleElement(std::shared_ptr<Nft> transducer, std::shared_ptr<Nfa> input_aut, unsigned input_index, std::shared_ptr<Nfa> output_aut, unsigned output_index)
                : transducer(transducer), input_aut(input_aut), input_index(input_index), output_aut(output_aut), output_index(output_index) { }
};

using TransducerNoodle = std::vector<TransducerNoodleElement>;

std::vector<TransducerNoodle> noodlify_for_transducer(
    std::shared_ptr<Nft> nft,
    const std::vector<std::shared_ptr<Nfa>>& input_automata,
    const std::vector<std::shared_ptr<Nfa>>& output_automata,
    bool reduce_intersection = true,
    bool use_homomorphic_heuristic = true
);

/**
 * @brief Process epsilon map to a sequence of values (sorted according to key desc)
 *
 * @param eps_cnt Epsilon count
 * @return Vector of keys (count of epsilons)
 */
VisitedEpsilonsCounterVector process_eps_map(const VisitedEpsilonsCounterMap& eps_cnt);

} // namespace SegNfa.

// Stuff related with replace operation in string solving
namespace replace {

/**
 * @brief Modify @p nfa in-place to remove outgoing transitions from final states.
 *
 * If @p nfa accepts empty string, returned NFA will accept only the empty string.
 * @param nfa NFA to modify.
 * @return The reluctant version of @p nfa.
 */
Nfa reluctant_nfa(Nfa nfa);

constexpr Symbol BEGIN_MARKER{ mata::nft::EPSILON - 100 }; ///< Marker marking the beginning of the regex to be replaced.
constexpr Symbol END_MARKER{ mata::nft::EPSILON - 99 }; ///< Marker marking the end of the regex to be replaced.

/**
 * How many occurrences of the regex to replace, in order from left to right?
 */
enum class ReplaceMode {
    Single, ///< Replace only the first occurrence of the regex.
    All, ///< Replace all occurrences of the regex.
};

/**
 * Create identity transducer over the @p alphabet with @p num_of_levels levels.
 */
Nft create_identity(mata::Alphabet* alphabet, size_t num_of_levels = 2);

/**
 * Create identity input/output transducer with 2 levels over the @p alphabet with @p level_cnt levels with single
 *  symbol @p from_symbol replaced with @to_symbol.
 */
Nft create_identity_with_single_symbol_replace(mata::Alphabet* alphabet, Symbol from_symbol, Symbol replacement,
                                               ReplaceMode replace_mode = ReplaceMode::All);

/**
 * Create identity input/output transducer with 2 levels over the @p alphabet with @p level_cnt levels with single
 *  symbol @p from_symbol replaced with word @p replacement.
 */
Nft create_identity_with_single_symbol_replace(mata::Alphabet* alphabet, Symbol from_symbol, const Word& replacement,
                                               ReplaceMode replace_mode = ReplaceMode::All);

/**
 * @brief Create NFT modelling a reluctant leftmost replace of regex @p regex to @p replacement.
 *
 * The most general replace operation, handling any regex as the part to be replaced.
 * @param regex A string containing regex to be replaced.
 * @param replacement Literal to be replaced with.
 * @param alphabet Alphabet over which to create the NFT.
 * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p regex.
 * @param begin_marker Symbol to be used internally as a begin marker of replaced @p regex.
 * @return The reluctant leftmost replace NFT.
 */
Nft replace_reluctant_regex(const std::string& regex, const Word& replacement, Alphabet* alphabet,
                            ReplaceMode replace_mode = ReplaceMode::All, Symbol begin_marker = BEGIN_MARKER);

/**
 * @brief Create NFT modelling a reluctant leftmost replace of regex represented by deterministic automaton @p aut to @p replacement.
 *
 * The most general replace operation, handling any regex as the part to be replaced.
 * @param aut deterministic automaton representing regex to be replaced.
 * @param replacement Literal to replace with.
 * @param alphabet Alphabet over which to create the NFT.
 * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p regex.
 * @param begin_marker Symbol to be used internally as a begin marker of replaced @p regex.
 * @return The reluctant leftmost replace NFT.
 */
Nft replace_reluctant_regex(nfa::Nfa aut, const Word& replacement, Alphabet* alphabet,
                            ReplaceMode replace_mode = ReplaceMode::All, Symbol begin_marker = BEGIN_MARKER);

/**
 * Create NFT modelling a reluctant leftmost replace of literal @p literal to @p replacement.
 * @param literal Literal to replace.
 * @param replacement Literal to replace with.
 * @param alphabet Alphabet over which to create the NFT.
 * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p literal.
 * @param end_marker Symbol to be used internally as an end marker marking the end of the replaced literal.
 * @return The reluctant leftmost replace NFT.
 */
Nft replace_reluctant_literal(const Word& literal, const Word& replacement, Alphabet* alphabet,
                              ReplaceMode replace_mode = ReplaceMode::All, Symbol end_marker = END_MARKER);

/**
 * Create NFT modelling a reluctant leftmost replace of symbol @p from_symbol to @p replacement.
 * @param from_symbol Symbol to replace.
 * @param replacement Symbol to replace with.
 * @param alphabet Alphabet over which to create the NFT.
 * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p from_symbol.
 * @return The reluctant leftmost replace NFT.
 */
Nft replace_reluctant_single_symbol(Symbol from_symbol, Symbol replacement, mata::Alphabet* alphabet,
                                    ReplaceMode replace_mode = ReplaceMode::All);

/**
 * Create NFT modelling a reluctant leftmost replace of symbol @p from_symbol to @p replacement.
 * @param from_symbol Symbol to replace.
 * @param replacement Literal to replace with.
 * @param alphabet Alphabet over which to create the NFT.
 * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p from_symbol.
 * @return The reluctant leftmost replace NFT.
 */
Nft replace_reluctant_single_symbol(Symbol from_symbol, const Word& replacement, mata::Alphabet* alphabet,
                                    ReplaceMode replace_mode = ReplaceMode::All);

/**
 * @brief Implementation of all reluctant replace versions.
 */
class ReluctantReplace {
public:
    /**
     * @brief Create NFT modelling a reluctant leftmost replace of regex represented by deterministic automaton @p aut to @p replacement.
     *
     * The most general replace operation, handling any regex as the part to be replaced.
     * @param aut Deterministic automaton representing regex to be replaced.
     * @param replacement Literal to replace with.
     * @param alphabet Alphabet over which to create the NFT.
     * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p regex.
     * @param begin_marker Symbol to be used internally as a begin marker of replaced @p regex.
     * @return The reluctant leftmost replace NFT.
     */
    static Nft replace_regex(nfa::Nfa aut, const Word& replacement, Alphabet* alphabet,
                             ReplaceMode replace_mode = ReplaceMode::All, Symbol begin_marker = BEGIN_MARKER);
    /**
     * Create NFT modelling a reluctant leftmost replace of literal @p literal to @p replacement.
     * @param literal Literal to replace.
     * @param replacement Literal to replace with.
     * @param alphabet Alphabet over which to create the NFT.
     * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p literal.
     * @param end_marker Symbol to be used internally as an end marker marking the end of the replaced literal.
     * @return The reluctant leftmost replace NFT.
     */
    static Nft replace_literal(const Word& literal, const Word& replacement, Alphabet* alphabet,
                                            ReplaceMode replace_mode = ReplaceMode::All, Symbol end_marker = END_MARKER);
    /**
     * Create NFT modelling a reluctant leftmost replace of symbol @p from_symbol to @p replacement.
     * @param from_symbol Symbol to replace.
     * @param replacement Symbol to replace with.
     * @param alphabet Alphabet over which to create the NFT.
     * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p from_symbol.
     * @return The reluctant leftmost replace NFT.
     */
    static Nft replace_symbol(Symbol from_symbol, Symbol replacement, mata::Alphabet* alphabet,
                                           ReplaceMode replace_mode = ReplaceMode::All);
    /**
     * Create NFT modelling a reluctant leftmost replace of symbol @p from_symbol to @p replacement.
     * @param from_symbol Symbol to replace.
     * @param replacement Literal to replace with.
     * @param alphabet Alphabet over which to create the NFT.
     * @param replace_mode Whether to replace all or just the single (the leftmost) occurrence of @p from_symbol.
     * @return The reluctant leftmost replace NFT.
     */
    static Nft replace_symbol(Symbol from_symbol, const Word& replacement, mata::Alphabet* alphabet,
                                           ReplaceMode replace_mode = ReplaceMode::All);
protected:
    nfa::Nfa end_marker_dfa(nfa::Nfa regex);
    Nft marker_nft(const nfa::Nfa& marker_dfa, Symbol marker);

    nfa::Nfa generic_marker_dfa(const std::string& regex, Alphabet* alphabet);
    nfa::Nfa generic_marker_dfa(nfa::Nfa regex, Alphabet* alphabet);

    nfa::Nfa begin_marker_nfa(const std::string& regex, Alphabet* alphabet);
    nfa::Nfa begin_marker_nfa(nfa::Nfa regex, Alphabet* alphabet);

    Nft begin_marker_nft(const nfa::Nfa& marker_nfa, Symbol begin_marker);
    Nft end_marker_dft(const nfa::Nfa& end_marker_dfa, Symbol end_marker);
    nfa::Nfa reluctant_nfa_with_marker(nfa::Nfa nfa, Symbol marker, Alphabet* alphabet);

    Nft reluctant_leftmost_nft(const std::string& regex, Alphabet* alphabet, Symbol begin_marker, const Word& replacement, ReplaceMode replace_mode);
    Nft reluctant_leftmost_nft(nfa::Nfa nfa, Alphabet* alphabet, Symbol begin_marker, const Word& replacement, ReplaceMode replace_mode);

    Nft replace_literal_nft(const Word& literal, const Word& replacement, const Alphabet* alphabet, Symbol end_marker,
                            ReplaceMode replace_mode = ReplaceMode::All);
};

} // namespace mata::applications::strings::replace

} // namespace mata::applications::strings.

#endif // MATA_STRING_SOLVING_HH_.
